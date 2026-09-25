"""Intelligent Query planning module with conversational context resolution."""

import re
from typing import Dict, Any, Optional, List
from ai_analyst.state.agent_state import AgentIntent


class QueryPlanner:
    """Extracts entities, dimensions, metrics, filters, and chart intent from natural language."""

    @staticmethod
    def plan(question: str, intent: str, conversation_context: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        q_lower = question.lower().strip()
        context = conversation_context or []
        
        # Check if question is a follow-up referencing previous context
        is_followup = False
        prev_question = ""
        if context and len(context) >= 1:
            prev_msg = context[-1]
            prev_question = (prev_msg.get("content") or "").lower()
            if any(p in q_lower for p in ["now show", "only top", "what about", "and for", "in rj", "in sp", "filter by", "just the", "show top"]):
                is_followup = True

        # 1. Detect Intent & Chart Hint
        detected_intent = intent
        chart_hint = None

        if any(w in q_lower for w in ["distribution", "histogram", "spread", "bins", "range of"]):
            detected_intent = AgentIntent.DISTRIBUTION.value
            chart_hint = "histogram"
        elif any(w in q_lower for w in ["related to", "relationship", "correlation", "versus", "vs", "against", "scatter"]) and not any(w in q_lower for w in ["month", "year", "top", "rank"]):
            detected_intent = AgentIntent.CORRELATION.value
            chart_hint = "scatter"
        elif any(w in q_lower for w in ["percentage", "share", "split", "proportion", "composition", "breakdown by payment", "payment channel", "order status composition"]):
            detected_intent = AgentIntent.PROPORTION_SHARE.value
            chart_hint = "donut"
        elif any(w in q_lower for w in ["month", "monthly", "trend", "daily", "timeline", "over time", "history", "trajectory", "cancellation rate"]):
            detected_intent = AgentIntent.TIME_SERIES.value
            chart_hint = "line"
        elif any(w in q_lower for w in ["top", "highest", "best", "leader", "ranking", "most", "lowest", "compare", "longest", "shortest"]):
            detected_intent = AgentIntent.RANKING.value
            chart_hint = "bar"

        # 2. Detect Metric
        metric = "GMV"
        agg = "SUM"
        target_table = "analytics_obt_orders"

        if "cancellation rate" in q_lower or "cancell" in q_lower:
            metric = "cancellation_rate"
            agg = "AVG"
            target_table = "analytics_obt_orders"
        elif any(w in q_lower for w in ["repeat", "returning"]):
            metric = "repeat_customer_rate"
            agg = "AVG"
            target_table = "dim_customer"
        elif any(w in q_lower for w in ["segment", "rfm"]):
            metric = "segment_spending"
            agg = "SUM"
            target_table = "dim_customer"
        elif any(w in q_lower for w in ["freight cost", "freight value", "shipping cost"]):
            metric = "freight_cost"
            agg = "AVG"
            target_table = "analytics_obt_orders"
        elif any(w in q_lower for w in ["delivery duration", "transit time", "delivery time", "transit duration", "days to deliver"]):
            metric = "delivery_duration"
            agg = "AVG"
            target_table = "analytics_obt_orders"
        elif any(w in q_lower for w in ["late", "delay", "sla", "on-time", "ontime"]):
            metric = "late_delivery_rate"
            agg = "AVG"
            target_table = "analytics_obt_orders"
        elif any(w in q_lower for w in ["review", "rating", "score", "csat", "star"]):
            metric = "review_score"
            agg = "AVG"
            target_table = "analytics_obt_orders"
        elif any(w in q_lower for w in ["aov", "average order value"]):
            metric = "AOV"
            agg = "AVG"
            target_table = "analytics_obt_orders"
        elif any(w in q_lower for w in ["payment value", "payment amount", "payment channel"]):
            metric = "payment_value"
            agg = "SUM"
            target_table = "fact_payments"
        elif any(w in q_lower for w in ["order count", "order volume", "how many orders", "total orders", "number of orders"]):
            metric = "orders"
            agg = "COUNT"
            target_table = "analytics_obt_orders"
        elif any(w in q_lower for w in ["unique customer", "buyers", "customer count"]):
            metric = "unique_customers"
            agg = "COUNT"
            target_table = "dim_customer"
        else:
            metric = "GMV"
            agg = "SUM"
            target_table = "analytics_obt_orders"

        # 3. Detect Dimension & Group By
        dimension = None
        group_by = None

        if detected_intent == AgentIntent.DISTRIBUTION.value:
            if "order value" in q_lower or "price" in q_lower or "revenue" in q_lower or "gmv" in q_lower:
                dimension = "order_value_distribution"
            elif "freight" in q_lower:
                dimension = "freight_distribution"
            else:
                dimension = "delivery_duration_distribution"
            group_by = ["bin_range"]
        elif detected_intent == AgentIntent.CORRELATION.value:
            if "freight" in q_lower and ("delivery" in q_lower or "duration" in q_lower or "time" in q_lower):
                dimension = "freight_vs_delivery_duration"
            elif "price" in q_lower and "review" in q_lower:
                dimension = "price_vs_review_score"
            elif "seller" in q_lower:
                dimension = "seller_volume_vs_review_score"
            else:
                dimension = "freight_vs_delivery_duration"
        elif any(w in q_lower for w in ["month", "monthly", "over time", "timeline"]):
            dimension = "purchase_month"
            group_by = ["purchase_year", "purchase_month", "purchase_month_name"]
        elif any(w in q_lower for w in ["category", "categories", "product type", "product"]):
            dimension = "category_name"
            group_by = ["category_name"]
        elif any(w in q_lower for w in ["payment", "payment method", "credit card", "boleto"]):
            dimension = "primary_payment_type"
            group_by = ["primary_payment_type"]
            target_table = "fact_payments"
        elif any(w in q_lower for w in ["status", "order status", "composition"]):
            dimension = "order_status"
            group_by = ["order_status"]
            target_table = "fact_orders"
        elif any(w in q_lower for w in ["state", "states", "destination state", "region", "geography"]):
            dimension = "customer_state"
            group_by = ["customer_state"]
        elif any(w in q_lower for w in ["seller", "merchant", "sellers"]):
            dimension = "seller_id"
            group_by = ["seller_id"]
            target_table = "dim_seller"
        elif any(w in q_lower for w in ["segment", "rfm", "customer tier"]):
            dimension = "rfm_segment"
            group_by = ["rfm_segment"]
            target_table = "dim_customer"

        # Inherit dimension from previous context if follow-up
        if is_followup and dimension is None:
            if any(w in prev_question for w in ["category", "product"]):
                dimension = "category_name"
                group_by = ["category_name"]
            elif any(w in prev_question for w in ["seller", "merchant"]):
                dimension = "seller_id"
                group_by = ["seller_id"]
                target_table = "dim_seller"
            elif any(w in prev_question for w in ["state"]):
                dimension = "customer_state"
                group_by = ["customer_state"]
            elif any(w in prev_question for w in ["month"]):
                dimension = "purchase_month"
                group_by = ["purchase_year", "purchase_month", "purchase_month_name"]

        # 4. Detect Filters (Year, State, Category)
        filters = {}
        year_match = re.search(r'\b(2016|2017|2018)\b', q_lower)
        if year_match:
            filters["purchase_year"] = int(year_match.group(1))

        state_match = re.search(r'\b(sp|rj|mg|pr|rs|sc|ba|df|es|go|pe|ce|pa|mt|ma|ms|pb|pi|rn|al|se|to|ro|am|ac|ap|rr)\b', q_lower)
        if state_match:
            filters["customer_state"] = state_match.group(1).upper()

        # 5. Detect Limit
        limit = 20
        limit_match = re.search(r'\btop\s+(\d+)\b', q_lower)
        if limit_match:
            limit = int(limit_match.group(1))
        elif any(w in q_lower for w in ["top five", "top 5"]):
            limit = 5
        elif any(w in q_lower for w in ["top ten", "top 10"]):
            limit = 10
        elif any(w in q_lower for w in ["top three", "top 3"]):
            limit = 3
        elif detected_intent == AgentIntent.KPI_LOOKUP.value or (dimension is None and not group_by):
            limit = 1
        elif detected_intent == AgentIntent.CORRELATION.value:
            limit = 100

        plan = {
            "metric": metric,
            "dimension": dimension,
            "filters": filters,
            "aggregation": agg,
            "group_by": group_by,
            "order_by": "metric_val" if group_by else None,
            "order_direction": "DESC",
            "limit": limit,
            "target_table_or_view": target_table,
            "intent": detected_intent,
            "chart_hint": chart_hint,
            "is_followup": is_followup
        }
        return plan


query_planner = QueryPlanner()
