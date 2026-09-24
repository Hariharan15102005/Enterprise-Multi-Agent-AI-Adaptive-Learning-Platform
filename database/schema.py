from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Date, DateTime, Text, PrimaryKeyConstraint, Index
)
from database.connection import Base

class DimGeolocation(Base):
    __tablename__ = "dim_geolocation"
    zip_code_prefix = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    city_canonical = Column(String(100), nullable=False)
    state_code = Column(String(2), nullable=False, index=True)
    brazil_macro_region = Column(String(20), nullable=False, index=True)
    sample_points_count = Column(Integer, default=1)

class DimCustomer(Base):
    __tablename__ = "dim_customer"
    customer_unique_id = Column(String(32), primary_key=True)
    first_zip_code_prefix = Column(Integer)
    current_city = Column(String(100), nullable=False)
    current_state = Column(String(2), nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    first_order_timestamp = Column(DateTime)
    latest_order_timestamp = Column(DateTime)
    lifetime_order_count = Column(Integer, default=1)
    lifetime_spend_brl = Column(Float, default=0.0)
    is_repeat_customer = Column(Boolean, default=False)
    rfm_recency_days = Column(Integer)
    rfm_frequency_score = Column(Integer)
    rfm_monetary_score = Column(Integer)
    rfm_segment = Column(String(50), index=True)
    created_at = Column(DateTime)

class DimProduct(Base):
    __tablename__ = "dim_product"
    product_id = Column(String(32), primary_key=True)
    category_name_pt = Column(String(100), default="nao_informado")
    category_name_en = Column(String(100), default="uncategorized", index=True)
    name_length_chars = Column(Integer)
    description_length_chars = Column(Integer)
    photos_qty = Column(Integer, default=0)
    weight_g = Column(Float, default=0.0)
    length_cm = Column(Float, default=0.0)
    height_cm = Column(Float, default=0.0)
    width_cm = Column(Float, default=0.0)
    volume_cm3 = Column(Float)
    density_g_cm3 = Column(Float)
    size_tier = Column(String(20), default="Standard", index=True)
    created_at = Column(DateTime)

class DimSeller(Base):
    __tablename__ = "dim_seller"
    seller_id = Column(String(32), primary_key=True)
    seller_zip_code_prefix = Column(Integer, nullable=False)
    seller_city = Column(String(100), nullable=False)
    seller_state = Column(String(2), nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    first_active_date = Column(DateTime)
    total_orders_fulfilled = Column(Integer, default=0)
    total_sales_value_brl = Column(Float, default=0.0)
    avg_dispatch_time_hours = Column(Float)
    sla_breach_rate_pct = Column(Float)
    avg_review_score = Column(Float)
    seller_tier = Column(String(30), default="Standard", index=True)
    created_at = Column(DateTime)

class DimDate(Base):
    __tablename__ = "dim_date"
    date_key = Column(Integer, primary_key=True)
    full_date = Column(Date, unique=True, nullable=False)
    year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False, index=True)
    month_name = Column(String(15), nullable=False)
    week_of_year = Column(Integer, nullable=False)
    day_of_month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    day_name = Column(String(15), nullable=False)
    is_weekend = Column(Boolean, nullable=False)
    is_holiday_br = Column(Boolean, default=False)
    holiday_name = Column(String(100))

class FactOrders(Base):
    __tablename__ = "fact_orders"
    order_id = Column(String(32), primary_key=True)
    customer_id = Column(String(32), nullable=False)
    customer_unique_id = Column(String(32), nullable=False, index=True)
    order_status = Column(String(20), nullable=False, index=True)
    order_date_key = Column(Integer, nullable=False, index=True)
    purchase_timestamp = Column(DateTime, nullable=False)
    approved_timestamp = Column(DateTime)
    delivered_carrier_timestamp = Column(DateTime)
    delivered_customer_timestamp = Column(DateTime)
    estimated_delivery_timestamp = Column(DateTime, nullable=False)
    total_item_count = Column(Integer, default=1)
    unique_product_count = Column(Integer, default=1)
    unique_seller_count = Column(Integer, default=1)
    total_items_price_brl = Column(Float, nullable=False)
    total_freight_value_brl = Column(Float, nullable=False)
    gross_order_value_brl = Column(Float, nullable=False)
    total_payment_value_brl = Column(Float, nullable=False)
    payment_value_discrepancy_brl = Column(Float, default=0.0)
    primary_payment_type = Column(String(20))
    max_payment_installments = Column(Integer, default=1)
    payment_sequential_count = Column(Integer, default=1)
    total_delivery_duration_days = Column(Float)
    delivery_delay_vs_estimated_days = Column(Float)
    is_delivered_late = Column(Boolean, default=False, index=True)
    review_score = Column(Integer)
    has_review = Column(Boolean, default=False)
    review_creation_timestamp = Column(DateTime)
    review_answer_timestamp = Column(DateTime)

class FactOrderItems(Base):
    __tablename__ = "fact_order_items"
    order_id = Column(String(32), nullable=False)
    order_item_id = Column(Integer, nullable=False)
    customer_unique_id = Column(String(32), nullable=False, index=True)
    product_id = Column(String(32), nullable=False, index=True)
    seller_id = Column(String(32), nullable=False, index=True)
    order_date_key = Column(Integer, nullable=False, index=True)
    purchase_timestamp = Column(DateTime, nullable=False)
    approved_timestamp = Column(DateTime)
    shipping_limit_timestamp = Column(DateTime, nullable=False)
    delivered_carrier_timestamp = Column(DateTime)
    delivered_customer_timestamp = Column(DateTime)
    estimated_delivery_timestamp = Column(DateTime, nullable=False)
    item_price_brl = Column(Float, nullable=False)
    freight_value_brl = Column(Float, nullable=False)
    total_item_cost_brl = Column(Float, nullable=False)
    freight_ratio_pct = Column(Float, nullable=False)
    dispatch_lead_time_hours = Column(Float)
    carrier_transit_days = Column(Float)
    total_delivery_days = Column(Float)
    estimated_delivery_days = Column(Float)
    delivery_delay_days = Column(Float)
    is_delayed = Column(Boolean, default=False, index=True)
    is_seller_sla_breach = Column(Boolean, default=False)
    haversine_distance_km = Column(Float)
    is_interstate_shipment = Column(Boolean, default=False)
    order_status = Column(String(20), nullable=False)
    created_at = Column(DateTime)

    __table_args__ = (
        PrimaryKeyConstraint("order_id", "order_item_id"),
        Index("idx_fct_items_order_item", "order_id", "order_item_id"),
    )

class FactPayments(Base):
    __tablename__ = "fact_payments"
    order_id = Column(String(32), nullable=False, index=True)
    payment_sequential = Column(Integer, nullable=False)
    payment_type = Column(String(20), nullable=False, index=True)
    payment_installments = Column(Integer, default=1)
    payment_value_brl = Column(Float, nullable=False)
    order_date_key = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("order_id", "payment_sequential"),
    )

class FactReviews(Base):
    __tablename__ = "fact_reviews"
    review_id = Column(String(32), nullable=False)
    order_id = Column(String(32), nullable=False, index=True)
    review_score = Column(Integer, nullable=False, index=True)
    review_comment_title = Column(String(255))
    review_comment_message = Column(Text)
    has_comment_text = Column(Boolean, default=False)
    comment_length_chars = Column(Integer, default=0)
    sentiment_label = Column(String(20), index=True)
    sentiment_score = Column(Float)
    review_creation_date = Column(Date, nullable=False)
    review_answer_timestamp = Column(DateTime, nullable=False)
    response_delay_hours = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("review_id", "order_id"),
    )
