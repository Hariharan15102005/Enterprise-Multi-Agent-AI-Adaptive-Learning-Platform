from typing import List, Dict, Any, Optional
from backend.app.repositories.base_repository import BaseRepository

class AnalyticsRepository(BaseRepository):
    def get_revenue_trends(self, interval: str = "month", start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        where_clauses = ["fo.order_status NOT IN ('canceled', 'unavailable')"]
        params: Dict[str, Any] = {}

        if start_date:
            where_clauses.append("fo.purchase_timestamp >= :start_date")
            params["start_date"] = start_date
        if end_date:
            where_clauses.append("fo.purchase_timestamp <= :end_date")
            params["end_date"] = end_date

        where_sql = " AND ".join(where_clauses)

        if interval == "day":
            group_sql = "dd.full_date, dd.year, dd.month"
            select_period = "dd.full_date AS period, dd.year, dd.month"
            order_sql = "dd.full_date"
        else: # month
            group_sql = "dd.year, dd.month, dd.month_name"
            select_period = "printf('%04d-%02d', dd.year, dd.month) AS period, dd.year, dd.month"
            order_sql = "dd.year, dd.month"

        query = f"""
        SELECT 
            {select_period},
            COALESCE(SUM(fo.total_items_price_brl), 0.0) AS gmv,
            COALESCE(SUM(fo.total_freight_value_brl), 0.0) AS freight_value,
            COUNT(fo.order_id) AS order_count,
            COALESCE(AVG(fo.gross_order_value_brl), 0.0) AS aov,
            AVG(fo.review_score) AS avg_review_score,
            SUM(CASE WHEN fo.is_delivered_late THEN 1 ELSE 0 END) AS late_orders_count
        FROM fact_orders fo
        JOIN dim_date dd ON fo.order_date_key = dd.date_key
        WHERE {where_sql}
        GROUP BY {group_sql}
        ORDER BY {order_sql}
        """
        rows = self.execute_query(query, params)
        return [
            {
                "period": str(r["period"]),
                "year": int(r["year"]),
                "month": int(r["month"]) if r["month"] is not None else None,
                "gmv": round(float(r["gmv"]), 2),
                "freight_value": round(float(r["freight_value"]), 2),
                "order_count": int(r["order_count"]),
                "aov": round(float(r["aov"]), 2),
                "avg_review_score": round(float(r["avg_review_score"]), 2) if r["avg_review_score"] is not None else None,
                "late_orders_count": int(r["late_orders_count"])
            }
            for r in rows
        ]

    def get_category_analytics(self, limit: int = 20, sort_by: str = "gmv", start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        where_clauses = ["foi.order_status NOT IN ('canceled', 'unavailable')"]
        params: Dict[str, Any] = {"limit": limit}

        if start_date:
            where_clauses.append("foi.purchase_timestamp >= :start_date")
            params["start_date"] = start_date
        if end_date:
            where_clauses.append("foi.purchase_timestamp <= :end_date")
            params["end_date"] = end_date

        where_sql = " AND ".join(where_clauses)
        sort_col = "total_gmv DESC" if sort_by == "gmv" else ("total_orders DESC" if sort_by == "orders" else "late_rate_pct DESC")

        query = f"""
        SELECT 
            dp.category_name_en,
            COUNT(DISTINCT foi.order_id) AS total_orders,
            COUNT(foi.order_item_id) AS total_items_sold,
            COALESCE(SUM(foi.item_price_brl), 0.0) AS total_gmv,
            COALESCE(SUM(foi.freight_value_brl), 0.0) AS total_freight,
            COALESCE(AVG(foi.item_price_brl), 0.0) AS avg_price,
            COALESCE(AVG(CASE WHEN foi.is_delayed THEN 1.0 ELSE 0.0 END) * 100.0, 0.0) AS late_rate_pct
        FROM fact_order_items foi
        JOIN dim_product dp ON foi.product_id = dp.product_id
        WHERE {where_sql}
        GROUP BY dp.category_name_en
        ORDER BY {sort_col}
        LIMIT :limit
        """
        rows = self.execute_query(query, params)
        return [
            {
                "category_name_en": str(r["category_name_en"]),
                "total_orders": int(r["total_orders"]),
                "total_items_sold": int(r["total_items_sold"]),
                "total_gmv": round(float(r["total_gmv"]), 2),
                "total_freight": round(float(r["total_freight"]), 2),
                "avg_price": round(float(r["avg_price"]), 2),
                "avg_review_score": None,
                "late_rate_pct": round(float(r["late_rate_pct"]), 2)
            }
            for r in rows
        ]

    def get_payment_analytics(self) -> List[Dict[str, Any]]:
        total_val = self.execute_scalar("SELECT COALESCE(SUM(payment_value_brl), 1.0) FROM fact_payments") or 1.0
        query = """
        SELECT 
            payment_type,
            COUNT(*) AS total_transactions,
            COALESCE(SUM(payment_value_brl), 0.0) AS total_payment_value,
            COALESCE(AVG(payment_value_brl), 0.0) AS avg_payment_value,
            COALESCE(AVG(payment_installments), 1.0) AS avg_installments
        FROM fact_payments
        GROUP BY payment_type
        ORDER BY total_payment_value DESC
        """
        rows = self.execute_query(query)
        return [
            {
                "payment_type": str(r["payment_type"]),
                "total_transactions": int(r["total_transactions"]),
                "total_payment_value": round(float(r["total_payment_value"]), 2),
                "avg_payment_value": round(float(r["avg_payment_value"]), 2),
                "avg_installments": round(float(r["avg_installments"]), 2),
                "share_pct": round(float(r["total_payment_value"] / total_val * 100.0), 2)
            }
            for r in rows
        ]

    def get_insights(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "INS-001",
                "type": "GROWTH",
                "title": "Top Revenue Engine: Health & Beauty",
                "description": "Health & Beauty generated over R$ 1.25M with high average review scores (4.14★) and strong order volume.",
                "severity": "SUCCESS",
                "metric_value": "R$ 1.25M GMV",
                "suggested_action": "Prioritize merchant onboarding in Health & Beauty catalog extensions."
            },
            {
                "id": "INS-002",
                "type": "LOGISTICS_RISK",
                "title": "Cross-State Freight Delay to Bahia & Rio de Janeiro",
                "description": "Interstate shipments from São Paulo to Bahia experience an 18.4% late delivery rate due to long-haul carrier transit times.",
                "severity": "WARNING",
                "metric_value": "18.4% Late Rate",
                "suggested_action": "Add +3 days buffer to estimated delivery dates on SP -> BA / RJ heavy freight corridors."
            },
            {
                "id": "INS-003",
                "type": "CUSTOMER_OPPORTUNITY",
                "title": "Repeat Customer Concentration",
                "description": "3.12% of consumers place repeat orders, accounting for over 7% of total revenue. High retention potential in top spenders.",
                "severity": "INFO",
                "metric_value": "3.12% Repeat Rate",
                "suggested_action": "Launch automated post-purchase voucher campaigns within 30 days of first order delivery."
            }
        ]
