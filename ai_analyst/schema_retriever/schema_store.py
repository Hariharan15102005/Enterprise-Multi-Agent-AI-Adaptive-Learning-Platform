"""Schema retrieval and database introspection engine for OlistIQ AI Analyst."""

from typing import Dict, Any, List, Set

TABLE_METADATA: Dict[str, Dict[str, Any]] = {
    "analytics_obt_orders": {
        "description": "Pre-joined One Big Table containing orders, items, products, customers, and delivery flags.",
        "type": "view",
        "columns": {
            "order_id": "VARCHAR(32) PRIMARY KEY",
            "customer_unique_id": "VARCHAR(32) - Unique persistent customer identifier",
            "customer_city": "VARCHAR(100)",
            "customer_state": "VARCHAR(2) - Brazilian state code (SP, RJ, MG, etc.)",
            "customer_rfm_segment": "VARCHAR(50) - RFM segment label",
            "order_status": "VARCHAR(20) - 'delivered', 'shipped', 'canceled', etc.",
            "purchase_timestamp": "DATETIME - Purchase datetime",
            "purchase_year": "INTEGER - e.g. 2016, 2017, 2018",
            "purchase_month": "INTEGER - 1 to 12",
            "purchase_month_name": "VARCHAR(15) - 'January', 'February', etc.",
            "purchase_quarter": "INTEGER - 1 to 4",
            "purchase_day_name": "VARCHAR(15) - 'Monday', etc.",
            "is_holiday_br": "BOOLEAN - Brazilian national holiday flag",
            "gross_order_value_brl": "FLOAT - Total order gross value (items + freight)",
            "total_items_price_brl": "FLOAT - Total product merchandise value (GMV)",
            "total_freight_value_brl": "FLOAT - Total freight shipping cost",
            "total_item_count": "INTEGER - Number of items in order",
            "primary_payment_type": "VARCHAR(20) - 'credit_card', 'boleto', 'voucher', 'debit_card'",
            "max_payment_installments": "INTEGER - Maximum installment count",
            "total_delivery_duration_days": "FLOAT - Doorstep transit days",
            "delivery_delay_vs_estimated_days": "FLOAT - Delay days (>0 means late)",
            "is_delivered_late": "BOOLEAN - 1 if delivered after estimated date, 0 otherwise",
            "review_score": "INTEGER - 1 to 5 stars",
            "has_review": "BOOLEAN"
        }
    },
    "fact_orders": {
        "description": "Order-level grain fact table containing 99,441 marketplace orders.",
        "type": "table",
        "columns": {
            "order_id": "VARCHAR(32) PRIMARY KEY",
            "customer_unique_id": "VARCHAR(32) - Unique consumer identifier",
            "order_status": "VARCHAR(20)",
            "purchase_timestamp": "DATETIME",
            "total_items_price_brl": "FLOAT - Order GMV",
            "total_freight_value_brl": "FLOAT - Order freight",
            "gross_order_value_brl": "FLOAT - Total gross value",
            "primary_payment_type": "VARCHAR(20)",
            "total_delivery_duration_days": "FLOAT",
            "delivery_delay_vs_estimated_days": "FLOAT",
            "is_delivered_late": "BOOLEAN",
            "review_score": "INTEGER"
        }
    },
    "fact_order_items": {
        "description": "Item-level grain fact table containing 112,650 items purchased.",
        "type": "table",
        "columns": {
            "order_id": "VARCHAR(32)",
            "order_item_id": "INTEGER - Item sequence within order",
            "customer_unique_id": "VARCHAR(32)",
            "product_id": "VARCHAR(32) - Foreign key to dim_product",
            "seller_id": "VARCHAR(32) - Foreign key to dim_seller",
            "purchase_timestamp": "DATETIME",
            "item_price_brl": "FLOAT - Line item price (GMV grain)",
            "freight_value_brl": "FLOAT - Line item freight",
            "dispatch_lead_time_hours": "FLOAT",
            "is_delayed": "BOOLEAN",
            "is_seller_sla_breach": "BOOLEAN",
            "haversine_distance_km": "FLOAT - Buyer to seller distance",
            "is_interstate_shipment": "BOOLEAN"
        }
    },
    "dim_customer": {
        "description": "Consumer dimension containing 96,096 unique customer profiles.",
        "type": "table",
        "columns": {
            "customer_unique_id": "VARCHAR(32) PRIMARY KEY",
            "current_city": "VARCHAR(100)",
            "current_state": "VARCHAR(2)",
            "lifetime_order_count": "INTEGER - Total historical orders",
            "lifetime_spend_brl": "FLOAT - Total historical spend (LTV)",
            "is_repeat_customer": "BOOLEAN - True if lifetime_order_count > 1",
            "rfm_recency_days": "INTEGER",
            "rfm_segment": "VARCHAR(50)"
        }
    },
    "dim_product": {
        "description": "Product catalog dimension containing 32,951 normalized SKUs.",
        "type": "table",
        "columns": {
            "product_id": "VARCHAR(32) PRIMARY KEY",
            "category_name_en": "VARCHAR(100) - English standardized category",
            "category_name_pt": "VARCHAR(100)",
            "weight_g": "FLOAT",
            "volume_cm3": "FLOAT",
            "size_tier": "VARCHAR(20)"
        }
    },
    "dim_seller": {
        "description": "Seller dimension containing 3,095 active merchant profiles.",
        "type": "table",
        "columns": {
            "seller_id": "VARCHAR(32) PRIMARY KEY",
            "seller_city": "VARCHAR(100)",
            "seller_state": "VARCHAR(2)",
            "total_orders_fulfilled": "INTEGER",
            "total_sales_value_brl": "FLOAT - Merchant cumulative sales",
            "avg_dispatch_time_hours": "FLOAT",
            "sla_breach_rate_pct": "FLOAT",
            "avg_review_score": "FLOAT",
            "seller_tier": "VARCHAR(30)"
        }
    },
    "dim_date": {
        "description": "Calendar dimension containing 1,461 calendar days (2016-2019).",
        "type": "table",
        "columns": {
            "date_key": "INTEGER PRIMARY KEY (YYYYMMDD)",
            "full_date": "DATE",
            "year": "INTEGER",
            "quarter": "INTEGER",
            "month": "INTEGER",
            "month_name": "VARCHAR(15)",
            "day_name": "VARCHAR(15)",
            "is_weekend": "BOOLEAN",
            "is_holiday_br": "BOOLEAN",
            "holiday_name": "VARCHAR(100)"
        }
    },
    "fact_payments": {
        "description": "Payment transactions fact table containing 103,886 records.",
        "type": "table",
        "columns": {
            "order_id": "VARCHAR(32)",
            "payment_sequential": "INTEGER",
            "payment_type": "VARCHAR(20) - 'credit_card', 'boleto', 'voucher', 'debit_card'",
            "payment_installments": "INTEGER",
            "payment_value_brl": "FLOAT"
        }
    },
    "fact_reviews": {
        "description": "Customer reviews fact table containing 99,224 verified reviews.",
        "type": "table",
        "columns": {
            "review_id": "VARCHAR(32)",
            "order_id": "VARCHAR(32)",
            "review_score": "INTEGER (1 to 5)",
            "has_comment_text": "BOOLEAN",
            "sentiment_label": "VARCHAR(20)",
            "response_delay_hours": "FLOAT"
        }
    }
}


class SchemaStore:
    """Retrieves relevant schema context based on intent and query requirements."""

    @staticmethod
    def get_relevant_schema(intent: str, question: str) -> str:
        """Constructs targeted schema documentation to prevent context bloat."""
        q_lower = question.lower()
        selected_tables: Set[str] = set()

        # Always include primary analytical view by default for tabular analytical queries
        selected_tables.add("analytics_obt_orders")

        if any(w in q_lower for w in ["seller", "merchant", "dispatch"]):
            selected_tables.add("dim_seller")
            selected_tables.add("fact_order_items")
            
        if any(w in q_lower for w in ["product", "category", "sku", "weight", "volume"]):
            selected_tables.add("dim_product")
            selected_tables.add("fact_order_items")
            
        if any(w in q_lower for w in ["customer", "repeat", "retention", "user", "buyer", "rfm", "ltv"]):
            selected_tables.add("dim_customer")
            
        if any(w in q_lower for w in ["payment", "installment", "credit_card", "boleto", "voucher"]):
            selected_tables.add("fact_payments")
            
        if any(w in q_lower for w in ["review", "rating", "satisfaction", "score", "star", "csat"]):
            selected_tables.add("fact_reviews")
            
        if any(w in q_lower for w in ["holiday", "day of week", "weekend", "quarter"]):
            selected_tables.add("dim_date")

        # Format schema markdown
        lines = ["### Relevant Analytical Schema Context:"]
        for tbl in selected_tables:
            if tbl in TABLE_METADATA:
                meta = TABLE_METADATA[tbl]
                lines.append(f"\n**{meta['type'].upper()}: {tbl}** — {meta['description']}")
                lines.append("Columns:")
                for col, typ in meta["columns"].items():
                    lines.append(f"  - `{col}`: {typ}")

        return "\n".join(lines)


schema_store = SchemaStore()
