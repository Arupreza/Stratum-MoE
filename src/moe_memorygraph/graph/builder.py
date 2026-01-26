from langgraph.graph import StateGraph, END, START
from langgraph.constants import Send
from src.moe_memorygraph.graph.state import AgentState
from src.moe_memorygraph.gating.router import route_query
from src.moe_memorygraph.experts.vector import search_vector_memory
from src.moe_memorygraph.graph.nodes.synthesize import synthesize_answer

# Node Wrappers
async def vector_node(state: AgentState):
    results = await search_vector_memory(state["query"], tenant_id=state["tenant_id"])
    return {"expert_results": [{"expert_name": "vector_search", "data": results}]}

async def ltm_node(state: AgentState):
    return {"expert_results": [{"expert_name": "ltm_recall", "data": "No LTM data."}]}

# Routing
def route_to_experts(state: AgentState):
    routes = []
    for expert in state["selected_experts"]:
        if expert == "vector_search":
            routes.append(Send("vector_expert", {"query": state["query"], "tenant_id": state["tenant_id"]}))
        elif expert == "ltm_recall":
            routes.append(Send("ltm_expert", {"query": state["query"], "tenant_id": state["tenant_id"]}))
    return routes

# Graph
workflow = StateGraph(AgentState)
workflow.add_node("router", route_query)
workflow.add_node("vector_expert", vector_node)
workflow.add_node("ltm_expert", ltm_node)
workflow.add_node("synthesizer", synthesize_answer)

workflow.add_edge(START, "router")
workflow.add_conditional_edges("router", route_to_experts, ["vector_expert", "ltm_expert"])
workflow.add_edge("vector_expert", "synthesizer")
workflow.add_edge("ltm_expert", "synthesizer")
workflow.add_edge("synthesizer", END)

app = workflow.compile()