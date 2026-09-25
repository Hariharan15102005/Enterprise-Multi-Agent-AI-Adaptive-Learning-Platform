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
        total_customers = self.execute_scalar("SELECT COUNT(DISTINCT customer_unique_id) FROM dim_customer") or 1
        query = """
        WITH state_orders AS (
            SELECT 
                dc.current_state AS state_code,
                COUNT(DISTINCT dc.customer_unique_id) AS customer_count,
                COALESCE(SUM(dc.lifetime_spend_brl), 0.0) AS total_spend_brl,
                COALESCE(AVG(dc.lifetime_spend_brl), 0.0) AS avg_spend_per_customer,
                COALESCE(AVG(CASE WHEN dc.is_repeat_customer THEN 1.0 ELSE 0.0 END) * 100.0, 0.0) AS repeat_customer_rate,
                COALESCE(SUM(dc.lifetime_order_count), 0) AS total_orders,
                AVG(dc.latitude) AS latitude,
                AVG(dc.longitude) AS longitude
            FROM dim_customer dc
            GROUP BY dc.current_state
        ),
        state_reviews AS (
            SELECT 
                dc.current_state AS state_code,
                AVG(fo.review_score) AS avg_review_score
            FROM dim_customer dc
            JOIN fact_orders fo ON dc.customer_unique_id = fo.customer_unique_id
            WHERE fo.has_review = 1
            GROUP BY dc.current_state
        )
        SELECT 
            so.state_code,
            so.customer_count,
            so.total_spend_brl,
            so.avg_spend_per_customer,
            so.repeat_customer_rate,
            so.total_orders,
            sr.avg_review_score,
            so.latitude,
            so.longitude,
            RANK() OVER (ORDER BY so.customer_count DESC) as rank
        FROM state_orders so
        LEFT JOIN state_reviews sr ON so.state_code = sr.state_code
        ORDER BY so.customer_count DESC
        """
        rows = self.execute_query(query)
        state_meta = {
            "AC": {"name": "Acre", "region": "North"},
            "AL": {"name": "Alagoas", "region": "Northeast"},
            "AM": {"name": "Amazonas", "region": "North"},
            "AP": {"name": "Amapá", "region": "North"},
            "BA": {"name": "Bahia", "region": "Northeast"},
            "CE": {"name": "Ceará", "region": "Northeast"},
            "DF": {"name": "Distrito Federal", "region": "Central-West"},
            "ES": {"name": "Espírito Santo", "region": "Southeast"},
            "GO": {"name": "Goiás", "region": "Central-West"},
            "MA": {"name": "Maranhão", "region": "Northeast"},
            "MG": {"name": "Minas Gerais", "region": "Southeast"},
            "MS": {"name": "Mato Grosso do Sul", "region": "Central-West"},
            "MT": {"name": "Mato Grosso", "region": "Central-West"},
            "PA": {"name": "Pará", "region": "North"},
            "PB": {"name": "Paraíba", "region": "Northeast"},
            "PE": {"name": "Pernambuco", "region": "Northeast"},
            "PI": {"name": "Piauí", "region": "Northeast"},
            "PR": {"name": "Paraná", "region": "South"},
            "RJ": {"name": "Rio de Janeiro", "region": "Southeast"},
            "RN": {"name": "Rio Grande do Norte", "region": "Northeast"},
            "RO": {"name": "Rondônia", "region": "North"},
            "RR": {"name": "Roraima", "region": "North"},
            "RS": {"name": "Rio Grande do Sul", "region": "South"},
            "SC": {"name": "Santa Catarina", "region": "South"},
            "SE": {"name": "Sergipe", "region": "Northeast"},
            "SP": {"name": "São Paulo", "region": "Southeast"},
            "TO": {"name": "Tocantins", "region": "North"}
        }

        return [
            {
                "state_code": str(r["state_code"]),
                "state_name": state_meta.get(str(r["state_code"]), {}).get("name", str(r["state_code"])),
                "region": state_meta.get(str(r["state_code"]), {}).get("region", "Other"),
                "customer_count": int(r["customer_count"]),
                "percentage_of_total": round(float(r["customer_count"]) / float(total_customers) * 100.0, 2),
                "rank": int(r["rank"]) if r["rank"] is not None else 0,
                "total_spend_brl": round(float(r["total_spend_brl"]), 2),
                "avg_spend_per_customer": round(float(r["avg_spend_per_customer"]), 2),
                "total_orders": int(r["total_orders"]) if r["total_orders"] is not None else int(r["customer_count"]),
                "avg_review_score": round(float(r["avg_review_score"]), 2) if r["avg_review_score"] is not None else 4.0,
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
