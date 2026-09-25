"""Natural Language & Query Plan to SQL generator for OlistIQ AI Analyst."""

import os
import re
import logging
from typing import Dict, Any, Optional

from ai_analyst.config.ai_config import ai_config

logger = logging.getLogger("olistiq.ai_analyst.sql_generator")


class SQLGenerator:
    """Generates SQLite-compatible analytical SQL using query plans and LLM prompts."""

    @staticmethod
    def generate_sql_from_plan(plan: Dict[str, Any], question: str) -> str:
        """Deterministic query synthesizer mapping structured plan to standard SQL."""
        q_lower = question.lower().strip()
        metric = plan.get("metric", "GMV")
        dimension = plan.get("dimension")
        filters = plan.get("filters", {})
        limit = plan.get("limit", 20)
        table = plan.get("target_table_or_view", "analytics_obt_orders")

        # 1. Base Where Clause
        where_clauses = []
        if table in ["analytics_obt_orders"]:
            if metric not in ["cancellation_rate", "order_status"]:
                where_clauses.append("order_status NOT IN ('canceled', 'unavailable')")
        elif table in ["fact_orders", "fact_order_items"]:
            if metric not in ["cancellation_rate", "order_status"]:
                where_clauses.append("fo.order_status NOT IN ('canceled', 'unavailable')")

        if "purchase_year" in filters:
            year = filters["purchase_year"]
            if table == "analytics_obt_orders":
                where_clauses.append(f"purchase_year = {year}")
            else:
                where_clauses.append(f"strftime('%Y', purchase_timestamp) = '{year}'")

        if "customer_state" in filters:
            st = filters["customer_state"]
            if table == "analytics_obt_orders":
                where_clauses.append(f"customer_state = '{st}'")
            elif table == "dim_customer":
                where_clauses.append(f"current_state = '{st}'")

        where_sql = ("\nWHERE " + "\n  AND ".join(where_clauses)) if where_clauses else ""

        # -------------------------------------------------------------
        # SPECIAL CASE: Distributions / Histograms
        # -------------------------------------------------------------
        if dimension == "order_value_distribution":
            return """SELECT 
    CASE 
        WHEN total_items_price_brl < 50 THEN 'R$ 0 - 50'
        WHEN total_items_price_brl < 100 THEN 'R$ 50 - 100'
        WHEN total_items_price_brl < 200 THEN 'R$ 100 - 200'
        WHEN total_items_price_brl < 500 THEN 'R$ 200 - 500'
        ELSE 'R$ 500+'
    END AS bin_range,
    COUNT(order_id) AS order_count,
    MIN(total_items_price_brl) AS sort_order
FROM analytics_obt_orders
WHERE total_items_price_brl IS NOT NULL
GROUP BY bin_range
ORDER BY sort_order ASC;"""

        if dimension == "delivery_duration_distribution":
            return """SELECT 
    CASE 
        WHEN total_delivery_duration_days < 5 THEN '0-5 days'
        WHEN total_delivery_duration_days < 10 THEN '5-10 days'
        WHEN total_delivery_duration_days < 15 THEN '10-15 days'
        WHEN total_delivery_duration_days < 20 THEN '15-20 days'
        WHEN total_delivery_duration_days < 25 THEN '20-25 days'
        WHEN total_delivery_duration_days < 30 THEN '25-30 days'
        ELSE '30+ days'
    END AS bin_range,
    COUNT(order_id) AS order_count,
    MIN(total_delivery_duration_days) AS sort_order
FROM analytics_obt_orders
WHERE order_status = 'delivered' 
  AND total_delivery_duration_days IS NOT NULL
GROUP BY bin_range
ORDER BY sort_order ASC;"""

        if dimension == "freight_distribution":
            return """SELECT 
    CASE 
        WHEN total_freight_value_brl < 10 THEN 'R$ 0 - 10'
        WHEN total_freight_value_brl < 20 THEN 'R$ 10 - 20'
        WHEN total_freight_value_brl < 30 THEN 'R$ 20 - 30'
        WHEN total_freight_value_brl < 50 THEN 'R$ 30 - 50'
        ELSE 'R$ 50+'
    END AS bin_range,
    COUNT(order_id) AS order_count,
    MIN(total_freight_value_brl) AS sort_order
FROM analytics_obt_orders
WHERE total_freight_value_brl IS NOT NULL
GROUP BY bin_range
ORDER BY sort_order ASC;"""

        # -------------------------------------------------------------
        # SPECIAL CASE: Correlations & Scatter Plots
        # -------------------------------------------------------------
        if dimension == "freight_vs_delivery_duration":
            return """SELECT 
    ROUND(total_freight_value_brl, 2) AS freight_cost_brl,
    ROUND(total_delivery_duration_days, 1) AS delivery_duration_days,
    customer_state,
    order_id
FROM analytics_obt_orders
WHERE order_status = 'delivered'
  AND total_delivery_duration_days IS NOT NULL
  AND total_freight_value_brl > 0
ORDER BY RANDOM()
LIMIT 100;"""

        if dimension == "price_vs_review_score":
            return """SELECT 
    ROUND(total_items_price_brl, 2) AS item_price_brl,
    review_score,
    customer_state,
    order_id
FROM analytics_obt_orders
WHERE review_score IS NOT NULL
  AND total_items_price_brl > 0
ORDER BY RANDOM()
LIMIT 100;"""

        # -------------------------------------------------------------
        # SPECIAL CASE: Proportions & Shares (Pie / Donut)
        # -------------------------------------------------------------
        if dimension == "primary_payment_type" or "payment" in q_lower:
            return """SELECT 
    payment_type,
    payment_type AS primary_payment_type,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT order_id) AS transaction_count,
    ROUND(SUM(payment_value_brl), 2) AS total_payment_value_brl,
    ROUND(100.0 * SUM(payment_value_brl) / (SELECT SUM(payment_value_brl) FROM fact_payments), 2) AS value_share_pct
FROM fact_payments
GROUP BY payment_type
ORDER BY total_payment_value_brl DESC;"""

        if dimension == "order_status" or "order status" in q_lower or "status composition" in q_lower:
            return """SELECT 
    order_status,
    COUNT(order_id) AS order_count,
    ROUND(100.0 * COUNT(order_id) / (SELECT COUNT(*) FROM fact_orders), 2) AS share_pct
FROM fact_orders
GROUP BY order_status
ORDER BY order_count DESC;"""

        if dimension == "rfm_segment" or "segment" in q_lower:
            return """SELECT 
    rfm_segment,
    COUNT(customer_unique_id) AS customer_count,
    ROUND(SUM(lifetime_spend_brl), 2) AS total_segment_spend_brl,
    ROUND(AVG(lifetime_spend_brl), 2) AS avg_spend_per_customer_brl
FROM dim_customer
WHERE rfm_segment IS NOT NULL
GROUP BY rfm_segment
ORDER BY total_segment_spend_brl DESC;"""

        # -------------------------------------------------------------
        # SPECIAL CASE: Cancellation Rate over time
        # -------------------------------------------------------------
        if metric == "cancellation_rate":
            return """SELECT 
    purchase_year,
    purchase_month,
    purchase_month_name,
    COUNT(order_id) AS total_orders,
    SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) AS canceled_orders,
    ROUND(100.0 * SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) / COUNT(order_id), 2) AS cancellation_rate_pct
FROM analytics_obt_orders
GROUP BY purchase_year, purchase_month, purchase_month_name
ORDER BY purchase_year ASC, purchase_month ASC;"""

        # -------------------------------------------------------------
        # SPECIAL CASE: Product Category Analytics
        # -------------------------------------------------------------
        if dimension == "category_name":
            if "review" in q_lower or "score" in q_lower:
                return f"""SELECT 
    COALESCE(dp.category_name_en, 'Other') AS category_name,
    COUNT(fr.review_id) AS review_count,
    ROUND(AVG(fr.review_score), 2) AS avg_review_score,
    ROUND(SUM(foi.item_price_brl), 2) AS total_gmv_brl
FROM fact_reviews fr
JOIN fact_orders fo ON fr.order_id = fo.order_id
JOIN fact_order_items foi ON fo.order_id = foi.order_id
LEFT JOIN dim_product dp ON foi.product_id = dp.product_id
GROUP BY dp.category_name_en
HAVING review_count >= 50
ORDER BY avg_review_score DESC
LIMIT {limit};"""
            else:
                cat_where = "WHERE foi.order_status NOT IN ('canceled', 'unavailable')"
                if "purchase_year" in filters:
                    cat_where += f" AND strftime('%Y', foi.purchase_timestamp) = '{filters['purchase_year']}'"
                return f"""SELECT 
    COALESCE(dp.category_name_en, 'Other') AS category_name,
    COUNT(DISTINCT foi.order_id) AS total_orders,
    ROUND(SUM(foi.item_price_brl), 2) AS total_gmv_brl,
    ROUND(AVG(foi.item_price_brl), 2) AS avg_item_price_brl
FROM fact_order_items foi
LEFT JOIN dim_product dp ON foi.product_id = dp.product_id
{cat_where}
GROUP BY dp.category_name_en
ORDER BY total_gmv_brl DESC
LIMIT {limit};"""

        # -------------------------------------------------------------
        # SPECIAL CASE: Seller Analytics
        # -------------------------------------------------------------
        if dimension == "seller_id":
            return f"""SELECT 
    ds.seller_id,
    ds.seller_city,
    ds.seller_state,
    ds.total_orders_fulfilled,
    ROUND(ds.total_sales_value_brl, 2) AS total_sales_value_brl,
    ROUND(ds.avg_review_score, 2) AS avg_review_score,
    ROUND(ds.sla_breach_rate_pct, 1) AS sla_breach_rate_pct
FROM dim_seller ds
ORDER BY ds.total_sales_value_brl DESC
LIMIT {limit};"""

        # -------------------------------------------------------------
        # SPECIAL CASE: State / Geography Analytics
        # -------------------------------------------------------------
        if dimension == "customer_state":
            if "delivery" in q_lower or "transit" in q_lower or "longest" in q_lower or "days" in q_lower:
                return f"""SELECT 
    customer_state,
    COUNT(DISTINCT order_id) AS delivered_volume,
    ROUND(AVG(total_delivery_duration_days), 1) AS avg_delivery_days,
    ROUND(100.0 * AVG(CASE WHEN is_delivered_late = 1 THEN 1.0 ELSE 0.0 END), 1) AS late_delivery_rate_pct
FROM analytics_obt_orders
WHERE order_status = 'delivered' 
  AND total_delivery_duration_days IS NOT NULL
GROUP BY customer_state
ORDER BY avg_delivery_days DESC
LIMIT {limit};"""
            elif "poor review" in q_lower or "review" in q_lower:
                return f"""SELECT 
    customer_state,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_items_price_brl), 2) AS total_gmv_brl,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(100.0 * AVG(CASE WHEN is_delivered_late = 1 THEN 1.0 ELSE 0.0 END), 1) AS late_delivery_rate_pct
FROM analytics_obt_orders
WHERE customer_state IS NOT NULL
GROUP BY customer_state
HAVING total_orders >= 500
ORDER BY total_gmv_brl DESC
LIMIT {limit};"""
            else:
                return f"""SELECT 
    customer_state,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_items_price_brl), 2) AS total_gmv_brl,
    ROUND(AVG(total_items_price_brl), 2) AS avg_order_value_brl,
    ROUND(100.0 * AVG(CASE WHEN is_delivered_late = 1 THEN 1.0 ELSE 0.0 END), 1) AS late_delivery_rate_pct
FROM analytics_obt_orders{where_sql}
GROUP BY customer_state
ORDER BY total_gmv_brl DESC
LIMIT {limit};"""

        # -------------------------------------------------------------
        # SPECIAL CASE: Time-Series / Monthly Revenue Trends
        # -------------------------------------------------------------
        if dimension == "purchase_month" or "trend" in q_lower or "monthly" in q_lower:
            return f"""SELECT 
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

        # -------------------------------------------------------------
        # Single Aggregate KPIs
        # -------------------------------------------------------------
        if metric == "repeat_customer_rate" or "repeat" in q_lower:
            return """SELECT 
    COUNT(customer_unique_id) AS total_unique_customers,
    SUM(CASE WHEN is_repeat_customer = 1 THEN 1 ELSE 0 END) AS repeat_customers_count,
    ROUND(100.0 * AVG(CAST(is_repeat_customer AS FLOAT)), 2) AS repeat_customer_rate_pct
FROM dim_customer;"""

        if metric == "late_delivery_rate" or "late" in q_lower:
            return f"""SELECT 
    COUNT(order_id) AS total_delivered_orders,
    SUM(CASE WHEN is_delivered_late = 1 THEN 1 ELSE 0 END) AS late_orders_count,
    ROUND(100.0 * AVG(CASE WHEN is_delivered_late = 1 THEN 1.0 ELSE 0.0 END), 2) AS late_delivery_rate_pct,
    ROUND(AVG(CASE WHEN is_delivered_late = 1 THEN delivery_delay_vs_estimated_days ELSE NULL END), 1) AS avg_delay_days
FROM analytics_obt_orders
WHERE order_status = 'delivered';"""

        if metric == "review_score" or "csat" in q_lower or "rating" in q_lower:
            return """SELECT 
    COUNT(review_id) AS total_reviews,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(100.0 * SUM(CASE WHEN review_score >= 4 THEN 1 ELSE 0 END) / COUNT(review_id), 2) AS positive_review_pct
FROM fact_reviews;"""

        # Default Single KPI Total Lookup (e.g. Total GMV / Revenue)
        return f"""SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_items_price_brl), 2) AS total_gmv_brl,
    ROUND(SUM(gross_order_value_brl), 2) AS total_gov_brl,
    ROUND(AVG(total_items_price_brl), 2) AS avg_order_value_brl
FROM analytics_obt_orders{where_sql};"""

    def generate(
        self,
        question: str,
        plan: Dict[str, Any],
        schema_context: str,
        metric_context: str
    ) -> str:
        """Translates structured query context into clean analytical SQL."""
        # Check if environment has a configured LLM key
        gemini_api_key = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
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
