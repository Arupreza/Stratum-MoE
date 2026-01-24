import asyncio
import sys
from moe_memorygraph.experts.vector import vector_expert

async def run_search(query: str):
    print(f"🔎 Searching memory for: '{query}'")
    print("-" * 50)
    
    results = await vector_expert.search(query, limit=3)
    
    if not results:
        print("❌ No memories found.")
        return

    for i, res in enumerate(results, 1):
        print(f"[{i}] Intent: {res['intent'].upper()}")
        print(f"    User Asked: {res['content']}")
        print(f"    Agent Reply: {res['response']}")
        print("-" * 50)

if __name__ == "__main__":
    # Allow user to pass a query arg, or default to a test question
    user_query = sys.argv[1] if len(sys.argv) > 1 else "I want to cancel my order"
    asyncio.run(run_search(user_query))