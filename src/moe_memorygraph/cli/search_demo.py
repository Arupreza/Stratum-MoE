import asyncio
from moe_memorygraph.experts.vector import vector_expert

async def run_accuracy_test():
    # 1. Define a test question (Simulating a real user)
    # This phrasing is DIFFERENT from the CSV, so we test "Semantic" understanding.
    test_query = "I received a damaged item, how can I get my money back?"
    
    print(f"❓ User Question: '{test_query}'")
    print("---------------------------------------------------------")

    # 2. Run the Expert
    results = await vector_expert.search(test_query, limit=1)

    # 3. Analyze Results
    if not results:
        print("❌ No results found! Check your database.")
        return

    top_match = results[0]
    print(f"✅ Top Match Found!")
    print(f"📂 Category: {top_match['category']}")
    print(f"🧠 Intent:   {top_match['intent']}")
    print(f"🤖 Answer:   {top_match['response']}")
    print("---------------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(run_accuracy_test())