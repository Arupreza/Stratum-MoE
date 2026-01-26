from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.moe_memorygraph.core.config import settings
from src.moe_memorygraph.graph.state import AgentState

# Initialize LLM
llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)
parser = JsonOutputParser()

SYSTEM_PROMPT = """
You are the Router for a customer support brain. 
Analyze the query and strictly select the necessary experts.

Experts available:
- "vector_search": For finding similar past tickets, technical issues, or policy documents.
- "ltm_recall": For trends, aggregate data, or "how many times" questions.

Return a valid JSON object with:
1. "selected_experts": List[str]
2. "rationale": str (Why you chose them)
3. "confidence": float (0.0 to 1.0)
"""

# THIS IS THE FUNCTION PYTHON IS LOOKING FOR
async def route_query(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{query}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        decision = await chain.ainvoke({"query": state["query"]})
        
        # Validation fallback
        experts = decision.get("selected_experts", [])
        if not experts:
            experts = ["vector_search"]
            
        return {
            "selected_experts": experts,
            "gate_rationale": decision.get("rationale", "Auto-selection"),
            "gate_confidence": decision.get("confidence", 0.5)
        }
        
    except Exception as e:
        # Failsafe
        return {
            "selected_experts": ["vector_search"],
            "gate_rationale": f"Router Error: {str(e)}",
            "gate_confidence": 0.0
        }