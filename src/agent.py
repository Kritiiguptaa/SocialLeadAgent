from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import intent_classifier, agent_response, lead_collector

def router(state: AgentState):
    intent = state['intent']
    step = state.get('step')

    if step and step.startswith("ask_"):
        return "lead_collector"
    
    if intent == "high_intent":
        return "lead_collector"
    
    return "agent_response"

def entry_router(state: AgentState):
    step = state.get("step")
    if step and step.startswith("ask_"):
        return "lead_collector"
    return "classify"

workflow = StateGraph(AgentState)

workflow.add_node("classify", intent_classifier)
workflow.add_node("agent_response", agent_response)
workflow.add_node("lead_collector", lead_collector)

workflow.set_conditional_entry_point(
    entry_router,
    {"classify": "classify", "lead_collector": "lead_collector"}
)

workflow.add_conditional_edges(
    "classify",
    router,
    {"agent_response": "agent_response", "lead_collector": "lead_collector"}
)

workflow.add_edge("agent_response", END)
workflow.add_edge("lead_collector", END)

app = workflow.compile()