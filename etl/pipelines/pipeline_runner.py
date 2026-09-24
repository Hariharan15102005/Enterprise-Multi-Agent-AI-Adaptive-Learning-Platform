import time
import logging
from datetime import datetime
from config.settings import settings
from etl.ingestion.csv_reader import IngestionManager
from etl.validation.quality_engine import DataQualityEngine
from etl.transformations import (
    transform_geolocation,
    transform_products,
    transform_sellers,
    transform_customers,
    generate_date_dimension,
    transform_orders,
    transform_order_items,
    transform_payments,
    transform_reviews
)
from etl.loaders.db_loader import DatabaseLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("OlistIQ-ETL")

class ETLPipeline:
    def __init__(self):
        self.ingestion = IngestionManager()
        self.quality = DataQualityEngine()
        self.loader = DatabaseLoader()
        self.execution_report = {}

    def run(self) -> dict:
        start_time = time.time()
        logger.info("==================================================")
        logger.info("Starting OlistIQ Enterprise ETL & Dimensional Pipeline")
        logger.info("==================================================")

        # ----------------------------------------------------
        # Stage 1: Ingestion & Schema Validation
        # ----------------------------------------------------
        logger.info("Stage 1/7: Ingesting Raw CSV Datasets from archive/...")
        raw_data = self.ingestion.read_all_datasets()
        logger.info(f"Successfully ingested {len(raw_data)} datasets.")

        # ----------------------------------------------------
        # Stage 2: Pre-Transformation Data Quality Checks
        # ----------------------------------------------------
        logger.info("Stage 2/7: Running Data Quality & Validation Engine...")
        self.quality.validate_primary_key(raw_data["olist_orders_dataset.csv"], ["order_id"], "olist_orders_dataset.csv")
        self.quality.validate_primary_key(raw_data["olist_products_dataset.csv"], ["product_id"], "olist_products_dataset.csv")
        self.quality.validate_primary_key(raw_data["olist_sellers_dataset.csv"], ["seller_id"], "olist_sellers_dataset.csv")
        self.quality.validate_foreign_key(
            raw_data["olist_orders_dataset.csv"], "customer_id",
            raw_data["olist_customers_dataset.csv"], "customer_id",
            "orders", "customers"
        )
        self.quality.validate_foreign_key(
            raw_data["olist_order_items_dataset.csv"], "product_id",
            raw_data["olist_products_dataset.csv"], "product_id",
            "order_items", "products"
        )
        self.quality.validate_numeric_ranges(raw_data["olist_order_items_dataset.csv"], "price", 0.0, 100000.0, "order_items")
        self.quality.validate_numeric_ranges(raw_data["olist_order_reviews_dataset.csv"], "review_score", 1.0, 5.0, "order_reviews")

        # ----------------------------------------------------
        # Stage 3: Dimension Transformations
        # ----------------------------------------------------
        logger.info("Stage 3/7: Transforming Dimension Tables...")
        
        # 3.1 Geolocation Dimension
        dim_geo = transform_geolocation(raw_data["olist_geolocation_dataset.csv"])
        logger.info(f"dim_geolocation: Aggregated {len(raw_data['olist_geolocation_dataset.csv'])} rows -> {len(dim_geo)} unique zip prefixes.")

        # 3.2 Product Dimension
        dim_product = transform_products(
            raw_data["olist_products_dataset.csv"],
            raw_data["product_category_name_translation.csv"]
        )
        logger.info(f"dim_product: Processed {len(dim_product)} product SKUs with English category normalization.")

        # 3.3 Seller Dimension
        dim_seller = transform_sellers(
            raw_data["olist_sellers_dataset.csv"],
            dim_geo,
            raw_data["olist_order_items_dataset.csv"]
        )
        logger.info(f"dim_seller: Processed {len(dim_seller)} sellers with location coordinates.")

        # 3.4 Customer Dimension
        dim_customer = transform_customers(
            raw_data["olist_customers_dataset.csv"],
            dim_geo,
            raw_data["olist_orders_dataset.csv"],
            raw_data["olist_order_items_dataset.csv"]
        )
        logger.info(f"dim_customer: Transformed {len(dim_customer)} unique customer profiles with RFM segments.")

        # 3.5 Date Dimension
        dim_date = generate_date_dimension("2016-01-01", "2019-12-31")
        logger.info(f"dim_date: Generated calendar dimension with {len(dim_date)} days and Brazilian holidays.")

        # ----------------------------------------------------
        # Stage 4: Fact Table Transformations
        # ----------------------------------------------------
        logger.info("Stage 4/7: Transforming Fact Tables...")

        # 4.1 Fact Orders
        fact_orders = transform_orders(
            raw_data["olist_orders_dataset.csv"],
            raw_data["olist_customers_dataset.csv"],
            raw_data["olist_order_items_dataset.csv"],
            raw_data["olist_order_payments_dataset.csv"],
            raw_data["olist_order_reviews_dataset.csv"]
        )
        logger.info(f"fact_orders: Processed {len(fact_orders)} order summaries.")

        # 4.2 Fact Order Items
        fact_order_items = transform_order_items(
            raw_data["olist_order_items_dataset.csv"],
            raw_data["olist_orders_dataset.csv"],
            raw_data["olist_customers_dataset.csv"],
            raw_data["olist_sellers_dataset.csv"],
            dim_geo
        )
        logger.info(f"fact_order_items: Processed {len(fact_order_items)} item rows with Haversine distance and SLA metrics.")

        # 4.3 Fact Payments
        fact_payments = transform_payments(
            raw_data["olist_order_payments_dataset.csv"],
            raw_data["olist_orders_dataset.csv"]
        )
        logger.info(f"fact_payments: Processed {len(fact_payments)} payment installment records.")

        # 4.4 Fact Reviews
        fact_reviews = transform_reviews(
            raw_data["olist_order_reviews_dataset.csv"]
        )
        logger.info(f"fact_reviews: Processed {len(fact_reviews)} review records with sentiment categorization.")

        # ----------------------------------------------------
        # Stage 5: Database Loading & Idempotent Schema Creation
        # ----------------------------------------------------
        logger.info("Stage 5/7: Loading Dimensions & Facts into Database Warehouse...")
        self.loader.initialize_schema(drop_first=True)

        self.loader.load_table(dim_geo, "dim_geolocation")
        self.loader.load_table(dim_product, "dim_product")
        self.loader.load_table(dim_seller, "dim_seller")
        self.loader.load_table(dim_customer, "dim_customer")
        self.loader.load_table(dim_date, "dim_date")

        self.loader.load_table(fact_orders, "fact_orders")
        self.loader.load_table(fact_order_items, "fact_order_items")
        self.loader.load_table(fact_payments, "fact_payments")
        self.loader.load_table(fact_reviews, "fact_reviews")

        # ----------------------------------------------------
        # Stage 6: Analytical Views & One Big Table (OBT) Creation
        # ----------------------------------------------------
        logger.info("Stage 6/7: Creating Materialized Views & One Big Table (OBT)...")
        self.loader.create_analytical_views()

        # ----------------------------------------------------
        # Stage 7: Final Reconciliation & Quality Verification
        # ----------------------------------------------------
        logger.info("Stage 7/7: Reconciling Row Counts and Generating Quality Audit...")
        final_counts = self.loader.get_table_counts()
        duration = round(time.time() - start_time, 2)
        quality_summary = self.quality.get_summary()

        logger.info("==================================================")
        logger.info(f"ETL Pipeline Complete in {duration}s | Quality Score: {quality_summary['overall_quality_score']}/100")
        logger.info("Database Loaded Row Counts:")
        for tbl, count in final_counts.items():
            logger.info(f"  • {tbl}: {count:,} rows")
        logger.info("==================================================")

        self.execution_report = {
            "status": "SUCCESS",
            "execution_timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "database_url": settings.DATABASE_URL,
            "final_table_counts": final_counts,
            "data_quality_summary": quality_summary,
            "ingestion_summary": self.ingestion.get_ingestion_summary()
        }

        return self.execution_report
