"""Comprehensive test suite for OlistIQ Conversational AI Analyst (LangGraph NL2SQL)."""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

import pytest
import sqlite3
from ai_analyst.service import ai_service
from ai_analyst.security.guardrails import security_guardrails
from ai_analyst.planning.query_planner import query_planner
from ai_analyst.state.agent_state import ChartType, ResponseType


def test_ai_query_1_total_revenue_kpi():
    """1. 'What is our total revenue?' -> KPI card with actual GMV."""
    res = ai_service.process_query("What is our total revenue?")
    assert res.get("error") is None
    assert "total_gmv_brl" in res["data"][0]
    assert res["visualization"]["recommended_chart"] == ChartType.KPI.value
    assert res["response_type"] == ResponseType.KPI.value
    assert "R$" in res["answer"]
    assert float(res["data"][0]["total_gmv_brl"]) > 10000000.0  # ~13.22M BRL


def test_ai_query_2_payment_channel_share_donut():
    """2. 'Show payment channel share by payment value.' -> Donut / Pie chart."""
    res = ai_service.process_query("Show payment channel share by payment value.")
    assert res.get("error") is None
    assert len(res["data"]) >= 4
    assert res["visualization"]["recommended_chart"] in [ChartType.DONUT.value, ChartType.PIE.value]
    
    # Verify Credit Card is top channel
    cc = next((r for r in res["data"] if r.get("payment_type") == "credit_card"), None)
    assert cc is not None
    assert float(cc["value_share_pct"]) > 70.0


def test_ai_query_3_top_categories_bar():
    """3. 'Top 10 product categories by revenue.' -> Bar / Horizontal bar chart."""
    res = ai_service.process_query("Top 10 product categories by revenue.")
    assert res.get("error") is None
    assert len(res["data"]) == 10
    assert res["visualization"]["recommended_chart"] in [ChartType.BAR.value, ChartType.HORIZONTAL_BAR.value]
    assert "total_gmv_brl" in res["data"][0]
    assert "category_name" in res["data"][0]


def test_ai_query_4_monthly_sales_trend_line():
    """4. 'Show monthly sales trends.' -> Line / Area chronological time-series."""
    res = ai_service.process_query("Show monthly sales trends.")
    assert res.get("error") is None
    assert len(res["data"]) > 10
    assert res["visualization"]["recommended_chart"] in [ChartType.LINE.value, ChartType.AREA.value]
    assert "purchase_month_name" in res["data"][0] or "purchase_month" in res["data"][0]


def test_ai_query_5_freight_vs_delivery_scatter():
    """5. 'Is freight cost related to delivery duration?' -> Scatter plot."""
    res = ai_service.process_query("Is freight cost related to delivery duration?")
    assert res.get("error") is None
    assert res["visualization"]["recommended_chart"] == ChartType.SCATTER.value
    assert res["response_type"] == ResponseType.CORRELATION.value
    assert "freight_cost_brl" in res["data"][0]
    assert "delivery_duration_days" in res["data"][0]


def test_ai_query_6_delivery_duration_distribution_histogram():
    """6. 'Show the distribution of delivery duration.' -> Histogram binned chart."""
    res = ai_service.process_query("Show the distribution of delivery duration.")
    assert res.get("error") is None
    assert res["visualization"]["recommended_chart"] == ChartType.HISTOGRAM.value
    assert res["response_type"] == ResponseType.DISTRIBUTION.value
    assert "bin_range" in res["data"][0]
    assert "order_count" in res["data"][0]


def test_ai_query_7_state_delivery_transit_bar():
    """7. 'Which states have the longest delivery times?' -> Bar chart."""
    res = ai_service.process_query("Which states have the longest delivery times?")
    assert res.get("error") is None
    assert len(res["data"]) > 10
    assert res["visualization"]["recommended_chart"] in [ChartType.BAR.value, ChartType.HORIZONTAL_BAR.value]
    assert "avg_delivery_days" in res["data"][0]
    assert "customer_state" in res["data"][0]


def test_ai_query_8_order_status_composition_donut():
    """8. 'Show order status composition.' -> Donut chart."""
    res = ai_service.process_query("Show order status composition.")
    assert res.get("error") is None
    assert res["visualization"]["recommended_chart"] in [ChartType.DONUT.value, ChartType.PIE.value]
    deliv = next((r for r in res["data"] if r.get("order_status") == "delivered"), None)
    assert deliv is not None
    assert float(deliv["share_pct"]) > 95.0


def test_ai_query_9_top_20_sellers_table():
    """9. 'Give me the exact results for the top 20 sellers.' -> Data table."""
    res = ai_service.process_query("Give me the exact results for the top 20 sellers.")
    assert res.get("error") is None
    assert len(res["data"]) == 20
    assert res["visualization"]["recommended_chart"] == ChartType.TABLE.value
    assert "seller_id" in res["data"][0]
    assert "total_sales_value_brl" in res["data"][0]


def test_ai_query_10_conversational_followup_context():
    """10. Test conversational context follow-up 'Now show only the top five'."""
    context = [
        {"role": "user", "content": "What are the top 10 product categories by revenue?"},
        {"role": "assistant", "content": "Here are the top 10 product categories by GMV."}
    ]
    res = ai_service.process_query("Now show only the top five", conversation_context=context)
    assert res.get("error") is None
    assert len(res["data"]) == 5
    assert "category_name" in res["data"][0]


def test_ai_security_guardrail_rejection():
    """11. Test security guardrail rejects SQL injection and dangerous commands."""
    malicious_query = "DROP TABLE fact_orders; SELECT * FROM dim_customer"
    is_safe, reason = security_guardrails.inspect_input(malicious_query)
    assert is_safe is False
    
    res = ai_service.process_query(malicious_query)
    assert res.get("intent") == "SECURITY_REJECTED"
    assert "Security check failed" in str(res.get("error")) or "rejected" in str(res.get("answer")).lower()


if __name__ == "__main__":
    test_ai_query_1_total_revenue_kpi()
    test_ai_query_2_payment_channel_share_donut()
    test_ai_query_3_top_categories_bar()
    test_ai_query_4_monthly_sales_trend_line()
    test_ai_query_5_freight_vs_delivery_scatter()
    test_ai_query_6_delivery_duration_distribution_histogram()
    test_ai_query_7_state_delivery_transit_bar()
    test_ai_query_8_order_status_composition_donut()
    test_ai_query_9_top_20_sellers_table()
    test_ai_query_10_conversational_followup_context()
    test_ai_security_guardrail_rejection()
    print("ALL AI ANALYST CONVERSATIONAL TESTS PASSED!")
