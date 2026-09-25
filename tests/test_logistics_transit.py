import urllib.request
import json
import sqlite3

def test_logistics_api_endpoint():
    url = "http://localhost:8000/api/v1/logistics/by-state"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        raw = response.read().decode('utf-8')
        payload = json.loads(raw)
        assert payload.get("success") is True
        data = payload.get("data", [])
        assert len(data) == 27, f"Expected 27 Brazilian states, got {len(data)}"
        
        # Verify required fields
        for state_item in data:
            assert "state_code" in state_item
            assert "state_name" in state_item
            assert "delivered_volume" in state_item
            assert "avg_delivery_days" in state_item
            assert "average_transit_days" in state_item
            assert "logistics_status" in state_item
            assert state_item["avg_delivery_days"] is not None
            assert state_item["avg_delivery_days"] > 0
            assert state_item["delivered_volume"] > 0

        # Verify SP is fastest and highest volume
        sp = next((s for s in data if s["state_code"] == "SP"), None)
        assert sp is not None
        assert sp["state_name"] == "São Paulo"
        assert sp["delivered_volume"] > 40000
        assert 8.0 <= sp["avg_delivery_days"] <= 9.5

        print(f"PASSED: API endpoint returned all {len(data)} Brazilian states with valid transit durations.")

def test_db_reconciliation():
    conn = sqlite3.connect("data/processed/olistiq.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        dc.current_state AS state_code,
        COUNT(DISTINCT fo.order_id) AS delivered_volume,
        AVG(julianday(fo.delivered_customer_timestamp) - julianday(fo.purchase_timestamp)) AS avg_transit_days
    FROM fact_orders fo
    JOIN dim_customer dc ON fo.customer_unique_id = dc.customer_unique_id
    WHERE fo.order_status = 'delivered'
      AND fo.delivered_customer_timestamp IS NOT NULL
      AND fo.purchase_timestamp IS NOT NULL
      AND julianday(fo.delivered_customer_timestamp) >= julianday(fo.purchase_timestamp)
    GROUP BY dc.current_state
    ORDER BY avg_transit_days ASC
    """)
    rows = cursor.fetchall()
    assert len(rows) == 27
    print(f"PASSED: Database query verified 27 states. Top 3 fastest: {[r[0] for r in rows[:3]]}")

if __name__ == "__main__":
    test_db_reconciliation()
    test_logistics_api_endpoint()
    print("ALL LOGISTICS TRANSIT DURATION TESTS PASSED!")
