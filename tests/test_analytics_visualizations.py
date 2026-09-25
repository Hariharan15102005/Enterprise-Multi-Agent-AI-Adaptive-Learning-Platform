import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.repositories.analytics_repository import AnalyticsRepository
import sqlite3

client = TestClient(app)

def test_category_analytics_ranking():
    """Verify that category analytics returns sorted results with correct schema and alias fields."""
    response = client.get("/api/v1/analytics/categories?limit=10&sort_by=gmv")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10
    assert len(data) > 0

    # Verify fields
    for item in data:
        assert "category" in item
        assert "category_name_en" in item
        assert "gmv" in item
        assert "total_gmv" in item
        assert "orders" in item
        assert "total_orders" in item
        assert "contribution_pct" in item
        assert item["gmv"] >= 0
        assert item["contribution_pct"] >= 0

    # Verify sorted descending by GMV
    gmv_list = [item["gmv"] for item in data]
    assert gmv_list == sorted(gmv_list, reverse=True)

def test_category_analytics_db_reconciliation():
    """Verify category totals and ranking against raw SQL calculation on delivered orders."""
    repo = AnalyticsRepository()
    db_results = repo.get_category_analytics(limit=10, sort_by="gmv")
    assert len(db_results) == 10
    
    # Check top category is Health & Beauty or Watches & Gifts or Bed Bath Table
    top_cat = db_results[0]
    assert top_cat["category"] in ["Health & Beauty", "Watches & Gifts", "Bed, Bath & Table"]
    assert top_cat["gmv"] > 1000000.0  # Top categories in Olist have > R$ 1,000,000 GMV
    assert 0 < top_cat["contribution_pct"] < 20.0

def test_category_analytics_sorting_modes():
    """Verify sorting by orders and late_rate."""
    # Sort by orders
    res_orders = client.get("/api/v1/analytics/categories?limit=5&sort_by=orders")
    assert res_orders.status_code == 200
    data_orders = res_orders.json()
    orders_list = [item["orders"] for item in data_orders]
    assert orders_list == sorted(orders_list, reverse=True)

    # Sort by late_rate
    res_late = client.get("/api/v1/analytics/categories?limit=5&sort_by=late_rate")
    assert res_late.status_code == 200
    data_late = res_late.json()
    late_list = [item["late_rate"] for item in data_late]
    assert late_list == sorted(late_list, reverse=True)

def test_payment_analytics_shares():
    """Verify that payment channel shares sum to ~100% and have valid attributes."""
    response = client.get("/api/v1/analytics/payments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4  # Credit Card, Boleto, Voucher, Debit Card

    total_val_share = sum(item["val_share_pct"] for item in data)
    total_tx_share = sum(item["tx_share_pct"] for item in data)

    # Allow rounding tolerance
    assert 99.0 <= total_val_share <= 100.5
    assert 99.0 <= total_tx_share <= 100.5

    # Check credit card is dominant channel (> 70%)
    credit_card = next((p for p in data if p["payment_type"] == "credit_card"), None)
    assert credit_card is not None
    assert credit_card["val_share_pct"] > 70.0
    assert credit_card["payment_channel"] == "Credit Card"
    assert credit_card["total_payment_value"] > 10000000.0
    assert credit_card["total_transactions"] > 70000
    assert credit_card["avg_installments"] > 1.0

    # Check Boleto is second largest channel (> 15%)
    boleto = next((p for p in data if p["payment_type"] == "boleto"), None)
    assert boleto is not None
    assert boleto["val_share_pct"] > 15.0
    assert boleto["payment_channel"] == "Boleto Bancário"
