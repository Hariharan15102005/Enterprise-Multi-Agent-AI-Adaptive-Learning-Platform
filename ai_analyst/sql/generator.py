"""Natural Language & Query Plan to SQL generator for OlistIQ AI Analyst."""

import os
import re
import logging
from typing import Dict, Any, Optional

from ai_analyst.config.ai_config import ai_config
from ai_analyst.planning.query_planner import QueryPlanner

logger = logging.getLogger("olistiq.ai_analyst.sql_generator")


class SQLGenerator:
    """Generates PostgreSQL/SQLite compatible SQL using query plans and LLM prompts."""

    @staticmethod
    def generate_sql_from_plan(plan: Dict[str, Any], question: str) -> str:
        """Deterministic query synthesizer mapping structured plan to standard SQL."""
        metric = plan.get("metric", "GMV")
        dimension = plan.get("dimension")
        filters = plan.get("filters", {})
        limit = plan.get("limit", 20)
        table = plan.get("target_table_or_view", "analytics_obt_orders")

        # 1. Base Column Expressions & Aggregations
        where_clauses = []
        
        # Exclude canceled orders for sales/gmv calculations by default
        if table in ["analytics_obt_orders"]:
            where_clauses.append("order_status NOT IN ('canceled', 'unavailable')")
        elif table in ["fact_orders", "fact_order_items"]:
            where_clauses.append("fo.order_status NOT IN ('canceled', 'unavailable')")

        for k, v in filters.items():
            if k == "purchase_year":
                if table == "analytics_obt_orders":
                    where_clauses.append(f"purchase_year = {v}")
                elif table in ["fact_orders", "fact_order_items"]:
                    where_clauses.append(f"strftime('%Y', fo.purchase_timestamp) = '{v}'")

        where_sql = ("\nWHERE " + "\n  AND ".join(where_clauses)) if where_clauses else ""

        # Specialized queries based on dimension and metric
        if dimension == "category_name":
            cat_where = "WHERE foi.order_status NOT IN ('canceled', 'unavailable')"
            if "purchase_year" in filters:
                cat_where += f" AND strftime('%Y', foi.purchase_timestamp) = '{filters['purchase_year']}'"
            sql = f"""SELECT 
    COALESCE(dp.category_name_en, 'uncategorized') AS category_name,
    COUNT(DISTINCT foi.order_id) AS total_orders,
    ROUND(SUM(foi.item_price_brl), 2) AS total_gmv_brl,
    ROUND(AVG(foi.item_price_brl), 2) AS avg_item_price_brl
FROM fact_order_items foi
LEFT JOIN dim_product dp ON foi.product_id = dp.product_id
{cat_where}
GROUP BY dp.category_name_en
ORDER BY total_gmv_brl DESC
LIMIT {limit};"""
            return sql

        if dimension == "seller_id":
            if "review" in question.lower() or "score" in question.lower():
                sql = f"""SELECT 
    ds.seller_id,
    ds.seller_city,
    ds.seller_state,
    ds.total_orders_fulfilled,
    ROUND(ds.avg_review_score, 2) AS avg_review_score,
    ROUND(ds.total_sales_value_brl, 2) AS total_sales_value_brl
FROM dim_seller ds
WHERE ds.total_orders_fulfilled >= 10
ORDER BY ds.avg_review_score DESC, ds.total_orders_fulfilled DESC
LIMIT {limit};"""
            elif "delay" in question.lower() or "late" in question.lower() or "sla" in question.lower():
                sql = f"""SELECT 
    ds.seller_id,
    ds.seller_city,
    ds.seller_state,
    ds.total_orders_fulfilled,
    ROUND(ds.sla_breach_rate_pct, 2) AS sla_breach_rate_pct,
    ROUND(ds.avg_dispatch_time_hours, 1) AS avg_dispatch_time_hours
FROM dim_seller ds
WHERE ds.total_orders_fulfilled >= 10
ORDER BY ds.sla_breach_rate_pct DESC
LIMIT {limit};"""
            else:
                sql = f"""SELECT 
    ds.seller_id,
    ds.seller_city,
    ds.seller_state,
    ds.total_orders_fulfilled,
    ROUND(ds.total_sales_value_brl, 2) AS total_gmv_brl,
    ROUND(ds.avg_review_score, 2) AS avg_review_score
FROM dim_seller ds
ORDER BY ds.total_sales_value_brl DESC
LIMIT {limit};"""
            return sql

        if dimension == "purchase_month":
            sql = f"""SELECT 
    purchase_year,
    purchase_month,
    purchase_month_name,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_items_price_brl), 2) AS total_gmv_brl,
    ROUND(AVG(total_items_price_brl), 2) AS avg_order_value_brl
FROM analytics_obt_orders{where_sql}
GROUP BY purchase_year, purchase_month, purchase_month_name
ORDER BY purchase_year ASC, purchase_month ASC
LIMIT {limit};"""
            return sql

        if dimension == "customer_state":
            sql = f"""SELECT 
    customer_state,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_items_price_brl), 2) AS total_gmv_brl,
    ROUND(100.0 * AVG(CASE WHEN is_delivered_late = 1 THEN 1.0 ELSE 0.0 END), 2) AS late_delivery_rate_pct
FROM analytics_obt_orders{where_sql}
GROUP BY customer_state
ORDER BY total_orders DESC
LIMIT {limit};"""
            return sql

        if dimension == "primary_payment_type":
            pay_where_clauses = where_clauses + ["primary_payment_type IS NOT NULL"]
            pay_where_sql = "\nWHERE " + "\n  AND ".join(pay_where_clauses)
            sql = f"""SELECT 
    primary_payment_type,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(gross_order_value_brl), 2) AS total_payment_value_brl,
    ROUND(100.0 * COUNT(DISTINCT order_id) / (SELECT COUNT(DISTINCT order_id) FROM analytics_obt_orders{where_sql}), 2) AS percentage_share
FROM analytics_obt_orders{pay_where_sql}
GROUP BY primary_payment_type
ORDER BY total_orders DESC
LIMIT {limit};"""
            return sql

        if metric == "repeat_customer_rate" or "repeat" in question.lower():
            sql = f"""SELECT 
    COUNT(customer_unique_id) AS total_unique_customers,
    SUM(CASE WHEN is_repeat_customer = 1 THEN 1 ELSE 0 END) AS repeat_customers_count,
    ROUND(100.0 * AVG(CAST(is_repeat_customer AS FLOAT)), 2) AS repeat_customer_rate_pct
FROM dim_customer;"""
            return sql

        if metric == "late_delivery_rate" or "late" in question.lower():
            late_clauses = ["order_status = 'delivered'"]
            if "purchase_year" in filters:
                late_clauses.append(f"purchase_year = {filters['purchase_year']}")
            late_where = "\nWHERE " + "\n  AND ".join(late_clauses)
            sql = f"""SELECT 
    COUNT(order_id) AS total_delivered_orders,
    SUM(CASE WHEN is_delivered_late = 1 THEN 1 ELSE 0 END) AS late_orders_count,
    ROUND(100.0 * AVG(CASE WHEN is_delivered_late = 1 THEN 1.0 ELSE 0.0 END), 2) AS late_delivery_rate_pct,
    ROUND(AVG(CASE WHEN is_delivered_late = 1 THEN delivery_delay_vs_estimated_days ELSE NULL END), 1) AS avg_delay_days
FROM analytics_obt_orders{late_where};"""
            return sql

        if metric == "csat" or "review" in question.lower() or "score" in question.lower():
            sql = f"""SELECT 
    COALESCE(dp.category_name_en, 'all_categories') AS category_name,
    COUNT(fr.review_id) AS total_reviews,
    ROUND(AVG(fr.review_score), 2) AS avg_review_score,
    ROUND(100.0 * SUM(CASE WHEN fr.review_score >= 4 THEN 1 ELSE 0 END) / COUNT(fr.review_id), 2) AS positive_review_pct
FROM fact_reviews fr
JOIN fact_orders fo ON fr.order_id = fo.order_id
LEFT JOIN fact_order_items foi ON fo.order_id = foi.order_id
LEFT JOIN dim_product dp ON foi.product_id = dp.product_id
GROUP BY dp.category_name_en
ORDER BY total_reviews DESC
LIMIT {limit};"""
            return sql

        # Default Single KPI Total Lookup (e.g. Total GMV in 2018)
        sql = f"""SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_items_price_brl), 2) AS total_gmv_brl,
    ROUND(SUM(gross_order_value_brl), 2) AS total_gov_brl,
    ROUND(AVG(total_items_price_brl), 2) AS avg_order_value_brl
FROM analytics_obt_orders{where_sql};"""
        return sql

    def generate(
        self,
        question: str,
        plan: Dict[str, Any],
        schema_context: str,
        metric_context: str
    ) -> str:
        """Translates structured query context into clean analytical SQL."""
        gemini_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain_core.messages import SystemMessage, HumanMessage

                llm = ChatGoogleGenerativeAI(
                    model=ai_config.LLM_MODEL,
                    temperature=ai_config.TEMPERATURE,
                    google_api_key=gemini_api_key
                )
                system_prompt = f"""You are a senior PostgreSQL data engineer for the OlistIQ decision platform.
Generate a SINGLE read-only SQL query to answer the user's business question.

{schema_context}

{metric_context}

RULES:
1. ONLY return raw SQL enclosed in ```sql ... ```. No conversational preamble.
2. Read-only queries only: SELECT, JOIN, GROUP BY, ORDER BY, WHERE, LIMIT.
3. Reference ONLY allowed tables: analytics_obt_orders, dim_customer, dim_seller, dim_product, fact_orders, fact_order_items, fact_payments, fact_reviews.
4. Always prefix join columns to avoid ambiguity (e.g. fo.order_status).
5. Always apply appropriate LIMIT (default 20).
"""
                response = llm.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Question: {question}\nQuery Plan: {plan}")
                ])
                content = response.content
                match = re.search(r"```(?:sql)?\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            except Exception as e:
                logger.warning("LLM generation encountered an issue, using deterministic planner fallback: %s", str(e))

        # Reliable, deterministic high-performance planner
        return self.generate_sql_from_plan(plan, question)


sql_generator = SQLGenerator()
