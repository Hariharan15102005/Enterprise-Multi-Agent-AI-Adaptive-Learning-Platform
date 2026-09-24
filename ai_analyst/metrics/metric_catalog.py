"""Centralized Business Metric Catalog for grounding AI Analyst queries."""

from typing import Dict, Any, List

BUSINESS_METRICS: Dict[str, Dict[str, Any]] = {
    "gmv": {
        "name": "Gross Merchandise Value (GMV)",
        "code": "MET-FIN-01",
        "description": "Total merchandise sales value excluding freight charges.",
        "sql_formula": "SUM(total_items_price_brl)",
        "unit": "BRL",
        "primary_view": "analytics_obt_orders"
    },
    "gov": {
        "name": "Gross Order Value (GOV)",
        "code": "MET-FIN-02",
        "description": "Total invoiced basket value (merchandise price + freight charges).",
        "sql_formula": "SUM(gross_order_value_brl)",
        "unit": "BRL",
        "primary_view": "analytics_obt_orders"
    },
    "aov": {
        "name": "Average Order Value (AOV)",
        "code": "MET-FIN-03",
        "description": "Average merchandise value per distinct customer order.",
        "sql_formula": "AVG(total_items_price_brl)",
        "unit": "BRL",
        "primary_view": "analytics_obt_orders"
    },
    "orders": {
        "name": "Order Volume",
        "code": "MET-OPS-01",
        "description": "Total count of unique completed orders.",
        "sql_formula": "COUNT(DISTINCT order_id)",
        "unit": "orders",
        "primary_view": "analytics_obt_orders"
    },
    "customers": {
        "name": "Total Unique Customers",
        "code": "MET-CUST-01",
        "description": "Count of distinct physical human consumers.",
        "sql_formula": "COUNT(DISTINCT customer_unique_id)",
        "unit": "customers",
        "primary_view": "dim_customer"
    },
    "repeat_customer_rate": {
        "name": "Repeat Customer Rate (%)",
        "code": "MET-CUST-02",
        "description": "Percentage of consumers with lifetime order count > 1.",
        "sql_formula": "100.0 * AVG(CAST(is_repeat_customer AS FLOAT))",
        "unit": "%",
        "primary_view": "dim_customer"
    },
    "late_delivery_rate": {
        "name": "Late Delivery Rate (%)",
        "code": "MET-LOG-01",
        "description": "Percentage of delivered orders arriving past estimated promise date.",
        "sql_formula": "100.0 * AVG(CASE WHEN is_delivered_late = 1 THEN 1.0 ELSE 0.0 END)",
        "unit": "%",
        "primary_view": "analytics_obt_orders"
    },
    "csat": {
        "name": "Customer Satisfaction Score (Average Review Score)",
        "code": "MET-CSAT-01",
        "description": "Mean review score on a 1.0 to 5.0 star scale.",
        "sql_formula": "AVG(review_score)",
        "unit": "stars",
        "primary_view": "analytics_obt_orders"
    },
    "freight_ratio": {
        "name": "Freight Ratio (%)",
        "code": "MET-LOG-02",
        "description": "Freight value as a percentage of total merchandise GMV.",
        "sql_formula": "100.0 * (SUM(total_freight_value_brl) / NULLIF(SUM(total_items_price_brl), 0))",
        "unit": "%",
        "primary_view": "analytics_obt_orders"
    }
}


class MetricCatalog:
    """Retrieves authoritative metric definitions and SQL aggregation expressions."""

    @staticmethod
    def get_relevant_metrics(question: str) -> str:
        q_lower = question.lower()
        matched: List[Dict[str, Any]] = []

        if any(w in q_lower for w in ["gmv", "revenue", "sales", "gross"]):
            matched.append(BUSINESS_METRICS["gmv"])
        if any(w in q_lower for w in ["order", "volume", "count", "transactions"]):
            matched.append(BUSINESS_METRICS["orders"])
        if any(w in q_lower for w in ["aov", "average order value", "basket size"]):
            matched.append(BUSINESS_METRICS["aov"])
        if any(w in q_lower for w in ["customer", "users", "buyers"]):
            matched.append(BUSINESS_METRICS["customers"])
        if any(w in q_lower for w in ["repeat", "retention", "returning"]):
            matched.append(BUSINESS_METRICS["repeat_customer_rate"])
        if any(w in q_lower for w in ["late", "delay", "sla", "on time", "transit"]):
            matched.append(BUSINESS_METRICS["late_delivery_rate"])
        if any(w in q_lower for w in ["review", "rating", "satisfaction", "score", "csat", "stars"]):
            matched.append(BUSINESS_METRICS["csat"])
        if any(w in q_lower for w in ["freight", "shipping cost"]):
            matched.append(BUSINESS_METRICS["freight_ratio"])

        if not matched:
            matched = [BUSINESS_METRICS["gmv"], BUSINESS_METRICS["orders"]]

        lines = ["### Authoritative Business Metric Formulas:"]
        for m in matched:
            lines.append(f"- **{m['name']} ({m['code']})**: `{m['sql_formula']}` ({m['description']})")

        return "\n".join(lines)


metric_catalog = MetricCatalog()
