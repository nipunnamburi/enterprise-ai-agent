from typing import Literal, Optional, Any
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import (
    analyze_request_node,
    create_plan_node,
    retrieve_context_node,
    select_tools_node,
    approval_gate_node,
    execute_tools_node,
    evaluate_results_node,
    generate_response_node,
    save_memory_node,
)


def route_after_select_tools(state: AgentState) -> Literal["approval_gate", "generate_response"]:
    pending = state.get("pending_tool_calls", [])
    if pending and len(pending) > 0:
        return "approval_gate"
    return "generate_response"


def route_after_evaluation(state: AgentState) -> Literal["generate_response", "select_tools"]:
    is_done = state.get("is_complete", False)
    iterations = state.get("iterations", 0)
    max_iter = state.get("max_iterations", 5)

    if is_done or iterations >= max_iter:
        return "generate_response"
    return "select_tools"


def build_enterprise_agent_graph(checkpointer: Optional[Any] = None):
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze_request", analyze_request_node)
    workflow.add_node("create_plan", create_plan_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("select_tools", select_tools_node)
    workflow.add_node("approval_gate", approval_gate_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("evaluate_results", evaluate_results_node)
    workflow.add_node("generate_response", generate_response_node)
    workflow.add_node("save_memory", save_memory_node)

    workflow.set_entry_point("analyze_request")

    workflow.add_edge("analyze_request", "create_plan")
    workflow.add_edge("create_plan", "retrieve_context")
    workflow.add_edge("retrieve_context", "select_tools")

    workflow.add_conditional_edges(
        "select_tools",
        route_after_select_tools,
        {
            "approval_gate": "approval_gate",
            "generate_response": "generate_response",
        },
    )

    workflow.add_edge("approval_gate", "execute_tools")
    workflow.add_edge("execute_tools", "evaluate_results")

    workflow.add_conditional_edges(
        "evaluate_results",
        route_after_evaluation,
        {
            "select_tools": "select_tools",
            "generate_response": "generate_response",
        },
    )

    workflow.add_edge("generate_response", "save_memory")
    workflow.add_edge("save_memory", END)

    return workflow.compile(checkpointer=checkpointer)


agent_graph = build_enterprise_agent_graph()
