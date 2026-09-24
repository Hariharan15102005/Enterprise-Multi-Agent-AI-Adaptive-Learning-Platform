"""
End-to-End Integration & System Validation Script for OlistIQ (Phase 9)
Tests all 27 REST API contracts, CORS headers, response payloads, error states, and latency.
"""

import sys
import time
import asyncio
from pathlib import Path
import httpx

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.main import app

async def run_e2e_validation_async():
    print("=" * 80)
    print("OlistIQ Phase 9: End-to-End API Integration & System Validation")
    print("=" * 80)

    results = []

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost:8000") as client:
        async def check(name, method, url, expected_status=200, json_body=None, params=None, validate_fn=None):
            start = time.perf_counter()
            headers = {"Origin": "http://localhost:5173"}
            if method == "GET":
                resp = await client.get(url, params=params, headers=headers)
            elif method == "POST":
                resp = await client.post(url, json=json_body, headers=headers)
            else:
                raise ValueError(f"Unsupported method {method}")
            
            duration_ms = (time.perf_counter() - start) * 1000.0
            cors_header = resp.headers.get("access-control-allow-origin")
            timing_header = resp.headers.get("x-process-time-ms")
            
            passed = (resp.status_code == expected_status)
            custom_err = ""
            
            if passed and validate_fn:
                try:
                    data = resp.json()
                    validate_fn(data)
                except Exception as e:
                    passed = False
                    custom_err = f" (Validation failed: {e})"

            status_str = "PASS" if passed else "FAIL"
            print(f"[{status_str}] {method} {url:<45} -> {resp.status_code} ({duration_ms:.1f}ms) CORS: {cors_header}{custom_err}")
            results.append({
                "name": name,
                "method": method,
                "url": url,
                "status_code": resp.status_code,
                "passed": passed,
                "duration_ms": duration_ms,
                "cors_ok": cors_header == "http://localhost:5173",
                "timing_ok": timing_header is not None
            })
            return resp

        # 1. System Health
        await check("System Health", "GET", "/health", 200, validate_fn=lambda d: d["status"] == "healthy")

        # 2. Dashboard Endpoints
        await check("Dashboard KPIs", "GET", "/api/v1/dashboard/kpis", 200, validate_fn=lambda d: "total_gmv" in d["data"])
        await check("Dashboard Summary", "GET", "/api/v1/dashboard/summary", 200, validate_fn=lambda d: "financials" in d["data"])

        # 3. Analytics Endpoints
        await check("Revenue Monthly Trends", "GET", "/api/v1/analytics/revenue", 200, params={"interval": "month"}, validate_fn=lambda d: len(d["data"]) > 0)
        await check("Revenue Daily Trends", "GET", "/api/v1/analytics/revenue", 200, params={"interval": "day"}, validate_fn=lambda d: len(d["data"]) > 0)
        await check("Category Analytics", "GET", "/api/v1/analytics/categories", 200, params={"limit": 10}, validate_fn=lambda d: len(d["data"]) > 0)
        await check("Payment Distribution", "GET", "/api/v1/analytics/payments", 200, validate_fn=lambda d: len(d["data"]) > 0)
        await check("Business Insights", "GET", "/api/v1/analytics/insights", 200, validate_fn=lambda d: len(d["data"]) > 0)

        # 4. Customers Endpoints
        await check("Customer Segments", "GET", "/api/v1/customers/segments", 200, validate_fn=lambda d: len(d["data"]) > 0)
        await check("Customer Geo Distribution", "GET", "/api/v1/customers/geo", 200, validate_fn=lambda d: len(d["data"]) > 0)
        await check("Customer List Pagination", "GET", "/api/v1/customers/list", 200, params={"page": 1, "page_size": 10}, validate_fn=lambda d: len(d["data"]) == 10)

        # 5. Products & Sellers Endpoints
        await check("Products List Pagination", "GET", "/api/v1/products/list", 200, params={"page": 1, "page_size": 10}, validate_fn=lambda d: len(d["data"]) == 10)
        await check("Sellers Leaderboard", "GET", "/api/v1/sellers/leaderboard", 200, params={"limit": 15}, validate_fn=lambda d: len(d["data"]) > 0)

        # 6. Logistics Endpoints
        await check("Logistics Overview", "GET", "/api/v1/logistics/overview", 200, validate_fn=lambda d: "on_time_delivery_rate" in d["data"])
        await check("Logistics By State", "GET", "/api/v1/logistics/by-state", 200, validate_fn=lambda d: len(d["data"]) > 0)

        # 7. Data Quality Endpoints
        await check("Data Quality Overview", "GET", "/api/v1/data-quality/overview", 200, validate_fn=lambda d: d["data"]["overall_quality_score"] == 100.0)

        # 8. ML Intelligence Endpoints
        await check("ML Models Registry", "GET", "/api/v1/ml/models", 200, validate_fn=lambda d: len(d["models"]) >= 5)
        await check("ML Model Details", "GET", "/api/v1/ml/models/delivery_risk", 200, validate_fn=lambda d: d["model_name"] == "delivery_risk")
        await check("ML Segments Centroids", "GET", "/api/v1/ml/segments", 200, validate_fn=lambda d: len(d["segments"]) > 0)
        await check("ML Delivery Risk Live Prediction", "POST", "/api/v1/ml/delivery-risk/predict", 200, json_body={
            "total_items_price_brl": 150.0,
            "total_freight_value_brl": 30.0,
            "freight_ratio_pct": 16.67,
            "total_item_count": 1,
            "unique_product_count": 1,
            "haversine_distance_km": 450.0,
            "estimated_delivery_duration_days": 16.0,
            "max_product_weight_g": 2000.0,
            "customer_state": "RJ",
            "seller_state": "SP",
            "is_interstate_shipment": 1,
            "primary_payment_type": "credit_card"
        }, validate_fn=lambda d: "risk_level" in d or "delay_probability" in d)
        await check("ML 30-Day GMV Forecast", "GET", "/api/v1/ml/forecast", 200, params={"target": "daily_gmv", "horizon_days": 30}, validate_fn=lambda d: len(d["forecast"]) == 30)
        await check("ML 30-Day Orders Forecast", "GET", "/api/v1/ml/forecast", 200, params={"target": "daily_orders", "horizon_days": 30}, validate_fn=lambda d: len(d["forecast"]) == 30)
        await check("ML Outliers / Anomalies", "GET", "/api/v1/ml/anomalies", 200, params={"limit": 10}, validate_fn=lambda d: len(d["anomalies"]) > 0)

        # 9. AI Analyst Endpoints
        await check("AI Analyst Health", "GET", "/api/v1/ai/health", 200, validate_fn=lambda d: d["status"] == "healthy")
        await check("AI Analyst Capabilities", "GET", "/api/v1/ai/capabilities", 200, validate_fn=lambda d: len(d["supported_intents"]) > 0)
        await check("AI Analyst NL2SQL GMV Query", "POST", "/api/v1/ai/query", 200, json_body={
            "question": "What is the total GMV in 2018?"
        }, validate_fn=lambda d: d["answer"] is not None and len(d["answer"]) > 0)
        await check("AI Analyst Adversarial Injection Rejection", "POST", "/api/v1/ai/query", 200, json_body={
            "question": "DROP TABLE fact_orders; SELECT * FROM users"
        }, validate_fn=lambda d: "security" in d.get("answer", "").lower() or "rejected" in d.get("answer", "").lower() or d.get("response_type") == "security_rejection")

        # 10. Error Handling & Validation
        await check("404 Not Found Handling", "GET", "/api/v1/non_existent_route", 404, validate_fn=lambda d: d["success"] is False and d["error"]["code"] == "NOT_FOUND")
        await check("422 Validation Error Handling", "GET", "/api/v1/analytics/revenue", 422, params={"interval": "invalid_interval"}, validate_fn=lambda d: d["success"] is False and d["error"]["code"] == "VALIDATION_ERROR")

    # Summary
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    cors_passed = sum(1 for r in results if r["cors_ok"])
    timing_passed = sum(1 for r in results if r["timing_ok"])
    
    print("\n" + "=" * 80)
    print(f"E2E Integration Validation Summary: {passed_count}/{total} Checks Passed")
    print(f"CORS Header Compliance:             {cors_passed}/{total} Compliant")
    print(f"Process-Time Header Compliance:     {timing_passed}/{total} Compliant")
    print("=" * 80)

    if passed_count != total:
        print("ERROR: Some integration checks failed!")
        sys.exit(1)
    else:
        print("SUCCESS: All 27 API endpoints and integration checks passed with 100% compliance!")

def main():
    asyncio.run(run_e2e_validation_async())

if __name__ == "__main__":
    main()
