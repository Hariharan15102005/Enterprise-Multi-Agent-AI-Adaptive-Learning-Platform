import os
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
from datetime import datetime
from config.settings import settings

EXPECTED_SCHEMAS = {
    "olist_customers_dataset.csv": [
        "customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"
    ],
    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"
    ],
    "olist_order_items_dataset.csv": [
        "order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"
    ],
    "olist_order_payments_dataset.csv": [
        "order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"
    ],
    "olist_order_reviews_dataset.csv": [
        "review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp"
    ],
    "olist_orders_dataset.csv": [
        "order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"
    ],
    "olist_products_dataset.csv": [
        "product_id", "product_category_name", "product_name_lenght", "product_description_lenght", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"
    ],
    "olist_sellers_dataset.csv": [
        "seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"
    ],
    "product_category_name_translation.csv": [
        "product_category_name", "product_category_name_english"
    ]
}

class IngestionManager:
    def __init__(self, raw_path: Path = settings.RAW_DATA_PATH):
        self.raw_path = raw_path
        self.ingestion_stats: Dict[str, dict] = {}

    def read_csv(self, filename: str) -> pd.DataFrame:
        file_path = self.raw_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Raw CSV file not found: {file_path}")

        df = pd.read_csv(file_path)
        expected_cols = EXPECTED_SCHEMAS.get(filename, [])
        
        # Schema verification
        missing_cols = set(expected_cols) - set(df.columns)
        if missing_cols:
            status = f"FAILED: Missing columns {missing_cols}"
            is_valid = False
        else:
            status = "PASSED"
            is_valid = True

        self.ingestion_stats[filename] = {
            "filename": filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "ingestion_timestamp": datetime.utcnow().isoformat(),
            "validation_status": status,
            "is_valid": is_valid
        }

        return df

    def read_all_datasets(self) -> Dict[str, pd.DataFrame]:
        datasets = {}
        for filename in EXPECTED_SCHEMAS.keys():
            datasets[filename] = self.read_csv(filename)
        return datasets

    def get_ingestion_summary(self) -> dict:
        return {
            "total_files": len(self.ingestion_stats),
            "all_valid": all(v["is_valid"] for v in self.ingestion_stats.values()),
            "files": self.ingestion_stats
        }
