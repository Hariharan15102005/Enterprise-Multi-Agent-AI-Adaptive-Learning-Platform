from typing import Dict, Any, Optional
from backend.app.repositories.base_repository import BaseRepository

class DashboardRepository(BaseRepository):
    def get_executive_kpis(self, start_date: Optional[str] = None, end_date: Optional[str] = None, state: Optional[str] = None) -> Dict[str, Any]:
        where_clauses = ["order_status NOT IN ('canceled', 'unavailable')"]
        params: Dict[str, Any] = {}

        if start_date:
            where_clauses.append("purchase_timestamp >= :start_date")
            params["start_date"] = start_date
        if end_date:
            where_clauses.append("purchase_timestamp <= :end_date")
            params["end_date"] = end_date
        if state:
            where_clauses.append("customer_state = :state")
            params["state"] = state

        where_sql = " AND ".join(where_clauses)

        query = f"""
        SELECT 
            COALESCE(SUM(total_items_price_brl), 0.0) AS gross_merchandise_value,
            COALESCE(COUNT(order_id), 0) AS total_orders,
            COALESCE(COUNT(DISTINCT customer_unique_id), 0) AS total_customers,
            COALESCE(AVG(gross_order_value_brl), 0.0) AS average_order_value,
            COALESCE(AVG(review_score), 0.0) AS average_review_score,
            COALESCE(SUM(total_freight_value_brl), 0.0) AS total_freight_value,
            COALESCE(AVG(CASE WHEN is_delivered_late THEN 1.0 ELSE 0.0 END) * 100.0, 0.0) AS late_delivery_rate,
            COALESCE(AVG(CASE WHEN is_delivered_late = 0 THEN 1.0 ELSE 0.0 END) * 100.0, 100.0) AS on_time_delivery_rate
        FROM analytics_obt_orders
        WHERE {where_sql}
        """
        kpi_row = self.execute_query(query, params)[0]

        # Total products and sellers
        prod_count = self.execute_scalar("SELECT COUNT(*) FROM dim_product") or 0
        seller_count = self.execute_scalar("SELECT COUNT(*) FROM dim_seller") or 0
        repeat_rate = self.execute_scalar("SELECT COALESCE(AVG(CASE WHEN is_repeat_customer THEN 1.0 ELSE 0.0 END) * 100.0, 0.0) FROM dim_customer") or 0.0

        return {
            "gross_merchandise_value": round(float(kpi_row["gross_merchandise_value"]), 2),
            "total_orders": int(kpi_row["total_orders"]),
            "total_customers": int(kpi_row["total_customers"]),
            "total_sellers": int(seller_count),
            "total_products": int(prod_count),
            "average_order_value": round(float(kpi_row["average_order_value"]), 2),
            "average_review_score": round(float(kpi_row["average_review_score"]), 2),
            "on_time_delivery_rate": round(float(kpi_row["on_time_delivery_rate"]), 2),
            "late_delivery_rate": round(float(kpi_row["late_delivery_rate"]), 2),
            "repeat_customer_rate": round(float(repeat_rate), 2),
            "total_freight_value": round(float(kpi_row["total_freight_value"]), 2)
        }
