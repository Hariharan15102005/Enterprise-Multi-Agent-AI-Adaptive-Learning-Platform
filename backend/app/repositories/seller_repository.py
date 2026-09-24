from typing import List, Dict, Any, Tuple, Optional
from backend.app.repositories.base_repository import BaseRepository

class SellerRepository(BaseRepository):
    def get_sellers_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        tier: Optional[str] = None,
        state: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        where_clauses = ["1=1"]
        params: Dict[str, Any] = {}

        if tier:
            where_clauses.append("seller_tier = :tier")
            params["tier"] = tier
        if state:
            where_clauses.append("seller_state = :state")
            params["state"] = state

        where_sql = " AND ".join(where_clauses)
        total = self.execute_scalar(f"SELECT COUNT(*) FROM dim_seller WHERE {where_sql}", params) or 0

        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        query = f"""
        SELECT 
            seller_id,
            seller_city,
            seller_state,
            seller_tier,
            total_orders_fulfilled AS orders_fulfilled,
            total_sales_value_brl,
            CASE WHEN total_orders_fulfilled > 0 THEN total_sales_value_brl / total_orders_fulfilled ELSE 0.0 END AS avg_order_value_brl,
            avg_dispatch_time_hours,
            sla_breach_rate_pct,
            avg_review_score
        FROM dim_seller
        WHERE {where_sql}
        ORDER BY total_sales_value_brl DESC
        LIMIT :limit OFFSET :offset
        """
        rows = self.execute_query(query, params)
        data = [
            {
                "seller_id": str(r["seller_id"]),
                "seller_city": str(r["seller_city"]),
                "seller_state": str(r["seller_state"]),
                "seller_tier": str(r["seller_tier"]),
                "orders_fulfilled": int(r["orders_fulfilled"]),
                "total_sales_value_brl": round(float(r["total_sales_value_brl"]), 2),
                "avg_order_value_brl": round(float(r["avg_order_value_brl"]), 2),
                "avg_dispatch_time_hours": round(float(r["avg_dispatch_time_hours"]), 1) if r["avg_dispatch_time_hours"] is not None else None,
                "sla_breach_rate_pct": round(float(r["sla_breach_rate_pct"]), 2) if r["sla_breach_rate_pct"] is not None else None,
                "avg_review_score": round(float(r["avg_review_score"]), 2) if r["avg_review_score"] is not None else None
            }
            for r in rows
        ]
        return data, int(total)
