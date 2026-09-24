"""Compiled LangGraph workflow for the OlistIQ AI Analyst."""

from langgraph.graph import StateGraph, END
from ai_analyst.state.agent_state import AgentState
from ai_analyst.graph.nodes import (
    check_security_node,
    classify_intent_node,
    route_ml_node,
    retrieve_schema_and_metrics_node,
    create_query_plan_node,
    generate_sql_node,
    validate_sql_node,
    execute_sql_node,
    repair_sql_node,
    generate_insights_node,
    format_response_node,
)
from ai_analyst.graph.edges import (
    check_security_edge,
    route_intent_edge,
    validate_sql_edge,
    execute_sql_edge,
)


def create_ai_analyst_graph():
    """Builds and compiles the production LangGraph state machine."""
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("check_security", check_security_node)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("route_ml", route_ml_node)
    workflow.add_node("retrieve_schema_and_metrics", retrieve_schema_and_metrics_node)
    workflow.add_node("create_query_plan", create_query_plan_node)
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_sql", validate_sql_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("repair_sql", repair_sql_node)
    workflow.add_node("generate_insights", generate_insights_node)
    workflow.add_node("format_response", format_response_node)

    # Set Entry Point
    workflow.set_entry_point("check_security")

    # Add Conditional & Direct Edges
    workflow.add_conditional_edges(
        "check_security",
        check_security_edge,
        {
            "format_response": "format_response",
            "classify_intent": "classify_intent",
        }
    )

    workflow.add_conditional_edges(
        "classify_intent",
        route_intent_edge,
        {
            "route_ml": "route_ml",
            "retrieve_schema_and_metrics": "retrieve_schema_and_metrics",
        }
    )

    workflow.add_edge("route_ml", "format_response")
    workflow.add_edge("retrieve_schema_and_metrics", "create_query_plan")
    workflow.add_edge("create_query_plan", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")

    workflow.add_conditional_edges(
        "validate_sql",
        validate_sql_edge,
        {
            "execute_sql": "execute_sql",
            "repair_sql": "repair_sql",
            "format_response": "format_response",
        }
    )

    workflow.add_edge("repair_sql", "validate_sql")

    workflow.add_conditional_edges(
        "execute_sql",
        execute_sql_edge,
        {
            "generate_insights": "generate_insights",
            "repair_sql": "repair_sql",
            "format_response": "format_response",
        }
    )

    workflow.add_edge("generate_insights", "format_response")
    workflow.add_edge("format_response", END)

    return workflow.compile()


# Global compiled graph instance
ai_analyst_graph = create_ai_analyst_graph()
