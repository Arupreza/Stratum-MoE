import asyncio
import os
# SYNTAX: 'load_dataset' is a versatile tool from Hugging Face.
# We use it here to read a local CSV file easily.
from datasets import load_dataset
from moe_memorygraph.db.session import AsyncSessionLocal
from moe_memorygraph.db.models import VectorMemory
from moe_memorygraph.core.embedding import embedder

async def ingest_local_csv(limit: int = 26872):
    """
    Reads a local CSV file and saves memories to Postgres.
    """
    # LOGIC: Define the path to your downloaded file.
    # We use a relative path so it works on any machine inside the project folder.
    local_csv_path = "data/raw/dataset.csv"
    
    # SYNTAX: os.path.exists()
    # LOGIC: Validation Check. Before trying to open the file, we ensure it exists.
    # If we skip this, the program will crash with a confusing 'FileNotFoundError' later.
    if not os.path.exists(local_csv_path):
        print(f"❌ Error: File not found at '{local_csv_path}'")
        print("   Run the wget command in your terminal first!")
        return

    print(f"📂 Loading data from local CSV: {local_csv_path}...")
    
    # SYNTAX: load_dataset("csv", data_files=..., split="train")
    # LOGIC:
    # 1. "csv": Tells the library to use its built-in CSV parser.
    # 2. data_files: Points to our local file on disk.
    # 3. split="train": As discussed, this extracts the list of rows from the 
    #    default "train" container, so we can loop over them directly.
    dataset = load_dataset("csv", data_files=local_csv_path, split="train")
    
    print(f"🚀 Starting ingestion of {limit} items...")

    # SYNTAX: The Context Manager (async with)
    # This creates a safe database session. It guarantees the connection is closed
    # automatically, even if an error occurs inside the block.
    async with AsyncSessionLocal() as session:
        count = 0
        
        # LOGIC: The Processing Loop
        # We iterate through the CSV data one row at a time.
        for row in dataset:
            if count >= limit:
                break # Stop processing once we reach our limit (e.g., 100)

            # SYNTAX: Dictionary Access
            # We grab the user's question from the "instruction" column of the CSV.
            text_content = row["instruction"]
            
            # LOGIC: The Transformation (Text -> Math)
            # We pass the text to our embedder service. 
            # It returns the "vector" (a list of 384 numbers).
            vector = embedder.embed_query(text_content)

            # SYNTAX: SQLAlchemy Model Construction
            # We build a Python object that matches our database table structure.
            memory_item = VectorMemory(
                tenant_id="demo_user",    # Required for multi-user support
                content=text_content,     # The searchable text
                embedding=vector,         # The math vector for pgvector
                # LOGIC: Metadata JSON
                # We pack the intent, category, and answer into a JSON dictionary.
                # This allows the AI to "read" the answer immediately after finding a match.
                metadata_={               
                    "intent": row["intent"],
                    "category": row["category"],
                    "response": row["response"]
                }
            )
            
            # SYNTAX: session.add()
            # This puts the object in the "Staging Area" (RAM). 
            # It is NOT saved to the database yet.
            session.add(memory_item)
            count += 1
            
            # LOGIC: Progress Indicator
            # Prints a message every 10 items so you know the script is working.
            if count % 10 == 0:
                print(f"🔹 Processed {count}/{limit} items...")

        # LOGIC: The Commit
        # We verify all 100 items are valid, then send ONE big signal to the database.
        # This is much faster than saving one item at a time.
        await session.commit()
        print(f"✅ Successfully ingested {count} memories from LOCAL CSV!")

# SYNTAX: Entry Point
# Since we are using 'async' functions, we need 'asyncio.run()' to start the event loop.
if __name__ == "__main__":
    asyncio.run(ingest_local_csv())