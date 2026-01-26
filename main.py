import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# --- 1. Robust Environment Loading ---
base_dir = Path(__file__).parent
env_path = base_dir / ".env"

print(f"🔍 Looking for .env at: {env_path}")

if not env_path.exists():
    print("❌ ERROR: .env file NOT found.")
    exit(1)

# READ RAW FILE CONTENT (To verify format)
print("\n--- 📄 RAW .ENV FILE CHECK ---")
try:
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            # Print the key part, mask the value
            if "=" in line:
                key, val = line.split("=", 1)
                masked_val = val.strip()[:5] + "..." if len(val.strip()) > 5 else "EMPTY"
                print(f"Line {i+1}: Found Key='{key.strip()}' | Value Starts With='{masked_val}'")
            else:
                print(f"Line {i+1}: [Ignored/Empty] {line.strip()}")
except Exception as e:
    print(f"❌ Error reading file raw: {e}")

# FORCE LOAD
print("\n--- 🔄 LOADING DOTENV ---")
load_dotenv(dotenv_path=env_path, override=True)

# --- 2. Verify Key ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ FAILURE: OPENAI_API_KEY is still None after loading.")
    print("👉 ACTION: Check your .env file format. It must be 'KEY=value' (no spaces around =).")
    exit(1)
else:
    print(f"✅ SUCCESS: API Key loaded! ({api_key[:8]}...)")

# --- 3. Run Graph ---
# We import inside the function to ensure env is loaded first
try:
    from src.moe_memorygraph.graph.builder import app
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    exit(1)

async def main():
    print("\n🧠 Starting Stratum-MoE Brain...")
    
    initial_state = {
        "query": "How do I reset my password?",
        "tenant_id": "demo_corp",
        "session_id": "sess_01",
        "expert_results": [] 
    }
    
    print(f"🔹 Processing Query: '{initial_state['query']}'")

    async for step in app.astream(initial_state):
        for node_name, result in step.items():
            print(f"✅ Node Completed: {node_name}")
            
            if node_name == "synthesizer":
                final = result.get('final_answer', {})
                print(f"\n📝 FINAL ANSWER:\n{final.get('answer')}\n")

if __name__ == "__main__":
    asyncio.run(main())