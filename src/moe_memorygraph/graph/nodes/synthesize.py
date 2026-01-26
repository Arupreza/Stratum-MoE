import json
from langchain_openai import ChatOpenAI
from src.moe_memorygraph.core.config import settings
from src.moe_memorygraph.graph.state import AgentState

# Initialize LLM
llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)

# THIS IS THE FUNCTION PYTHON IS LOOKING FOR
async def synthesize_answer(state: AgentState):
    """
    Node: Synthesizes the final answer using data from all experts.
    """
    # 1. Flatten expert results into a single context string
    context_str = ""
    for res in state["expert_results"]:
        expert_name = res.get('expert_name', 'unknown')
        data = res.get('data', 'no data')
        context_str += f"\n--- Expert: {expert_name} ---\n{data}\n"
    
    # 2. Construct Prompt
    prompt = f"""
    You are a helpful customer support agent. 
    Answer the user query based strictly on the context below.
    
    Format your response as a valid JSON object with two keys:
    1. "answer": The text response to the user.
    2. "confidence": A score (0.0-1.0).
    
    Context:
    {context_str}
    
    User Query: {state['query']}
    """
    
    # 3. Call LLM
    response = await llm.ainvoke(prompt)
    
    # 4. Parse Output (with failsafe)
    try:
        # Clean potential markdown from LLM (e.g., ```json ... ```)
        content = response.content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(content)
        
        return {
            "final_answer": parsed, 
            "answer_confidence": parsed.get("confidence", 0.0)
        }
    except:
        # Fallback for plain text response
        return {
            "final_answer": {"answer": response.content},
            "answer_confidence": 0.0
        }