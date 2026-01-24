import asyncio
from datasets import load_dataset
from moe_memorygraph.db.session import AsyncSessionLocal
from moe_memorygraph.db.models import VectorMemory
from moe_memorygraph.core.embedding import embedder

async def ingest_bitext_data(limit: int = 100):
    """
    Downloads Bitext dataset, generates embeddings, and saves to Postgres.
    limit: Number of rows to ingest (start small for testing).
    """
    print(f"🚀 Starting ingestion of {limit} items from Bitext dataset...")

    # 1. Load Data from Hugging Face
    # This dataset contains: instruction (user query), response (agent answer), intent, category
    dataset = load_dataset("bitext/Bitext-customer-support-llm-chatbot-training-dataset", split="train")

    async with AsyncSessionLocal() as session:
        count = 0
        
        # 2. Iterate through the dataset
        for row in dataset:
            if count >= limit:
                break

            text_content = row["instruction"]  # The User's Question
            
            # 3. Generate Embedding (The "Vibe" of the question)
            vector = embedder.embed_query(text_content)

            # 4. Create DB Object
            # We store the 'response' in metadata so the Agent can read it later.
            memory_item = VectorMemory(
                tenant_id="demo_user",    # Hardcoded for this demo
                content=text_content,     # The text we search against
                embedding=vector,         # The HNSW vector
                metadata_={               
                    "intent": row["intent"],
                    "category": row["category"],
                    "response": row["response"] # The "Gold Standard" answer
                }
            )
            
            session.add(memory_item)
            count += 1
            
            # Progress update
            if count % 10 == 0:
                print(f"🔹 Processed {count}/{limit} items...")

        # 5. Commit everything to the database
        await session.commit()
        print(f"✅ Successfully ingested {count} memories into PostgreSQL!")

if __name__ == "__main__":
    asyncio.run(ingest_bitext_data())