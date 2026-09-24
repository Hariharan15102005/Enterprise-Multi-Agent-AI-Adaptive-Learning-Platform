from typing import List, Dict, Any, Tuple, Optional
from backend.app.repositories.base_repository import BaseRepository

class CustomerRepository(BaseRepository):
    def get_segment_distribution(self) -> List[Dict[str, Any]]:
        total_customers = self.execute_scalar("SELECT COUNT(*) FROM dim_customer") or 1
        query = """
        SELECT 
            rfm_segment AS segment_name,
            COUNT(*) AS customer_count,
            COALESCE(SUM(lifetime_spend_brl), 0.0) AS total_spend_brl,
            COALESCE(AVG(rfm_recency_days), 0.0) AS avg_recency_days,
            COALESCE(AVG(lifetime_order_count), 1.0) AS avg_frequency,
            COALESCE(AVG(lifetime_spend_brl), 0.0) AS avg_monetary_spend
        FROM dim_customer
        GROUP BY rfm_segment
        ORDER BY total_spend_brl DESC
        """
        rows = self.execute_query(query)
        return [
            {
                "segment_name": str(r["segment_name"]),
                "customer_count": int(r["customer_count"]),
                "share_pct": round(float(r["customer_count"] / total_customers * 100.0), 2),
                "total_spend_brl": round(float(r["total_spend_brl"]), 2),
                "avg_recency_days": round(float(r["avg_recency_days"]), 1),
                "avg_frequency": round(float(r["avg_frequency"]), 2),
                "avg_monetary_spend": round(float(r["avg_monetary_spend"]), 2)
            }
            for r in rows
        ]

    def get_geo_distribution(self) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            dc.current_state AS state_code,
            COUNT(*) AS customer_count,
            COALESCE(SUM(dc.lifetime_spend_brl), 0.0) AS total_spend_brl,
            COALESCE(AVG(dc.lifetime_spend_brl), 0.0) AS avg_spend_per_customer,
            COALESCE(AVG(CASE WHEN dc.is_repeat_customer THEN 1.0 ELSE 0.0 END) * 100.0, 0.0) AS repeat_customer_rate,
            AVG(dc.latitude) AS latitude,
            AVG(dc.longitude) AS longitude
        FROM dim_customer dc
        GROUP BY dc.current_state
        ORDER BY customer_count DESC
        """
        rows = self.execute_query(query)
        return [
            {
                "state_code": str(r["state_code"]),
                "customer_count": int(r["customer_count"]),
                "total_spend_brl": round(float(r["total_spend_brl"]), 2),
                "avg_spend_per_customer": round(float(r["avg_spend_per_customer"]), 2),
                "repeat_customer_rate": round(float(r["repeat_customer_rate"]), 2),
                "latitude": round(float(r["latitude"]), 4) if r["latitude"] is not None else None,
                "longitude": round(float(r["longitude"]), 4) if r["longitude"] is not None else None
            }
            for r in rows
        ]

    def get_customers_paginated(self, page: int = 1, page_size: int = 20, segment: Optional[str] = None, state: Optional[str] = None) -> Tuple[List[Dict[str, Any]], int]:
        where_clauses = ["1=1"]
        params: Dict[str, Any] = {}

        if segment:
            where_clauses.append("rfm_segment = :segment")
            params["segment"] = segment
        if state:
            where_clauses.append("current_state = :state")
            params["state"] = state

        where_sql = " AND ".join(where_clauses)
        total = self.execute_scalar(f"SELECT COUNT(*) FROM dim_customer WHERE {where_sql}", params) or 0

        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        query = f"""
        SELECT 
            customer_unique_id,
            current_city,
            current_state,
            lifetime_order_count,
            lifetime_spend_brl,
            is_repeat_customer,
            rfm_recency_days,
            rfm_frequency_score,
            rfm_monetary_score,
            rfm_segment
        FROM dim_customer
        WHERE {where_sql}
        ORDER BY lifetime_spend_brl DESC
        LIMIT :limit OFFSET :offset
        """
        rows = self.execute_query(query, params)
        data = [
            {
                "customer_unique_id": str(r["customer_unique_id"]),
                "current_city": str(r["current_city"]),
                "current_state": str(r["current_state"]),
                "lifetime_order_count": int(r["lifetime_order_count"]),
                "lifetime_spend_brl": round(float(r["lifetime_spend_brl"]), 2),
                "is_repeat_customer": bool(r["is_repeat_customer"]),
                "rfm_recency_days": int(r["rfm_recency_days"]) if r["rfm_recency_days"] is not None else None,
                "rfm_frequency_score": int(r["rfm_frequency_score"]) if r["rfm_frequency_score"] is not None else None,
                "rfm_monetary_score": int(r["rfm_monetary_score"]) if r["rfm_monetary_score"] is not None else None,
                "rfm_segment": str(r["rfm_segment"]) if r["rfm_segment"] is not None else None
            }
            for r in rows
        ]
        return data, int(total)
