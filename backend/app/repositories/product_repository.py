from typing import List, Dict, Any, Tuple, Optional
from backend.app.repositories.base_repository import BaseRepository

class ProductRepository(BaseRepository):
    def get_products_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        sort_by: str = "items_sold"
    ) -> Tuple[List[Dict[str, Any]], int]:
        where_clauses = ["1=1"]
        params: Dict[str, Any] = {}

        if category:
            where_clauses.append("dp.category_name_en = :category")
            params["category"] = category

        where_sql = " AND ".join(where_clauses)
        total = self.execute_scalar(f"SELECT COUNT(*) FROM dim_product dp WHERE {where_sql}", params) or 0

        sort_col = "total_gmv_brl DESC" if sort_by == "gmv" else "items_sold DESC"
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        query = f"""
        SELECT 
            dp.product_id,
            dp.category_name_en,
            COUNT(foi.order_item_id) AS items_sold,
            COALESCE(SUM(foi.item_price_brl), 0.0) AS total_gmv_brl,
            COALESCE(AVG(foi.item_price_brl), 0.0) AS avg_price_brl,
            COALESCE(AVG(foi.freight_value_brl), 0.0) AS avg_freight_brl,
            dp.weight_g,
            dp.volume_cm3,
            dp.size_tier
        FROM dim_product dp
        LEFT JOIN fact_order_items foi ON dp.product_id = foi.product_id
        WHERE {where_sql}
        GROUP BY dp.product_id, dp.category_name_en, dp.weight_g, dp.volume_cm3, dp.size_tier
        ORDER BY {sort_col}
        LIMIT :limit OFFSET :offset
        """
        rows = self.execute_query(query, params)
        data = [
            {
                "product_id": str(r["product_id"]),
                "category_name_en": str(r["category_name_en"]),
                "items_sold": int(r["items_sold"]),
                "total_gmv_brl": round(float(r["total_gmv_brl"]), 2),
                "avg_price_brl": round(float(r["avg_price_brl"]), 2),
                "avg_freight_brl": round(float(r["avg_freight_brl"]), 2),
                "weight_g": round(float(r["weight_g"]), 1),
                "volume_cm3": round(float(r["volume_cm3"]), 1),
                "size_tier": str(r["size_tier"]),
                "avg_review_score": None
            }
            for r in rows
        ]
        return data, int(total)
