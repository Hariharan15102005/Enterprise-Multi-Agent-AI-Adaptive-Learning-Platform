"""Query planning module that constructs intermediate structured query plans."""

import re
from typing import Dict, Any, Optional
from ai_analyst.state.agent_state import QueryPlan, AgentIntent


class QueryPlanner:
    """Extracts entities, dimensions, metrics, and filters to formulate a structured QueryPlan."""

    @staticmethod
    def plan(question: str, intent: str) -> Dict[str, Any]:
        q_lower = question.lower()
        
        # 1. Detect Metric
        metric = "GMV"
        agg = "SUM"
        target_table = "analytics_obt_orders"
        
        if any(w in q_lower for w in ["repeat", "returning"]):
            metric = "repeat_customer_rate"
            agg = "AVG"
            target_table = "dim_customer"
        elif any(w in q_lower for w in ["customer", "buyers", "users"]):
            metric = "unique_customers"
            agg = "COUNT"
            target_table = "dim_customer"
        elif any(w in q_lower for w in ["late", "delay", "sla"]):
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
        elif any(w in q_lower for w in ["order count", "order volume", "how many orders", "total orders", "monthly orders", "orders in"]):
            metric = "orders"
            agg = "COUNT"
            target_table = "analytics_obt_orders"

        # 2. Detect Dimension & Group By
        dimension = None
        group_by = None
        
        if any(w in q_lower for w in ["month", "monthly"]):
            dimension = "purchase_month"
            group_by = ["purchase_year", "purchase_month", "purchase_month_name"]
        elif any(w in q_lower for w in ["year", "yearly", "annual"]):
            dimension = "purchase_year"
            group_by = ["purchase_year"]
        elif any(w in q_lower for w in ["category", "categories", "product type"]):
            dimension = "category_name"
            group_by = ["category_name"]
        elif any(w in q_lower for w in ["seller", "merchant", "sellers"]):
            dimension = "seller_id"
            group_by = ["seller_id"]
            if target_table == "analytics_obt_orders":
                target_table = "dim_seller"
        elif any(w in q_lower for w in ["state", "states", "region", "geography"]):
            dimension = "customer_state"
            group_by = ["customer_state"]
        elif any(w in q_lower for w in ["payment", "payment method", "installments"]):
            dimension = "primary_payment_type"
            group_by = ["primary_payment_type"]
        elif any(w in q_lower for w in ["segment", "rfm"]):
            dimension = "rfm_segment"
            group_by = ["rfm_segment"]
            target_table = "dim_customer"

        # 3. Detect Temporal Filters
        filters = {}
        year_match = re.search(r'\b(2016|2017|2018)\b', q_lower)
        if year_match:
            filters["purchase_year"] = int(year_match.group(1))

        # 4. Detect Limit
        limit = 20
        limit_match = re.search(r'\btop\s+(\d+)\b', q_lower)
        if limit_match:
            limit = int(limit_match.group(1))
        elif intent == AgentIntent.KPI_LOOKUP.value or (dimension is None and not group_by):
            limit = 1

        plan = {
            "metric": metric,
            "dimension": dimension,
            "filters": filters,
            "aggregation": agg,
            "group_by": group_by,
            "order_by": "metric_val" if group_by else None,
            "order_direction": "DESC",
            "limit": limit,
            "target_table_or_view": target_table
        }
        return plan


query_planner = QueryPlanner()
