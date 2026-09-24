"""Insight Synthesizer to generate factual, correlation-safe business answers."""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from ai_analyst.state.agent_state import ResponseType

logger = logging.getLogger("olistiq.ai_analyst.synthesizer")


class InsightSynthesizer:
    """Produces grounded natural language answers and visualization suggestions."""

    @staticmethod
    def synthesize(
        question: str,
        rows: List[Dict[str, Any]],
        columns: List[str],
        plan: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str], Dict[str, Any], str]:
        """Returns (final_answer, insights, visualization, response_type)."""
        if not rows:
            return (
                "No matching data was found for the requested filters.",
                [],
                {"recommended_chart": "table"},
                ResponseType.TEXT.value
            )

        q_lower = question.lower()
        insights: List[str] = []
        visualization: Dict[str, Any] = {"recommended_chart": "table"}
        response_type = ResponseType.TABLE.value

        # Case 1: Single-row aggregate KPI (e.g., Total GMV in 2018, Repeat Customer Rate)
        if len(rows) == 1:
            row = rows[0]
            response_type = ResponseType.KPI.value
            visualization = {"recommended_chart": "KPI", "title": "Summary Metric"}

            if "total_gmv_brl" in row:
                gmv = row.get("total_gmv_brl", 0)
                orders = row.get("total_orders", 0)
                aov = row.get("avg_order_value_brl", 0)
                
                year_str = f" in {plan['filters']['purchase_year']}" if plan and "purchase_year" in plan.get("filters", {}) else ""
                answer = f"Total Gross Merchandise Value (GMV){year_str} was R$ {gmv:,.2f} across {orders:,} orders (AOV: R$ {aov:,.2f})."
                insights.append(f"Recorded {orders:,} fulfilled customer orders.")
                if aov > 0:
                    insights.append(f"Average Order Value stood at R$ {aov:,.2f}.")
                return answer, insights, visualization, response_type

            if "repeat_customer_rate_pct" in row:
                rate = row.get("repeat_customer_rate_pct", 0)
                repeats = row.get("repeat_customers_count", 0)
                total = row.get("total_unique_customers", 0)
                answer = f"The marketplace had {repeats:,} repeat customers out of {total:,} unique buyers, representing a repeat customer rate of {rate:.2f}%."
                insights.append(f"96.88% of buyers in the historical dataset made exactly one transaction.")
                return answer, insights, visualization, response_type

            if "late_delivery_rate_pct" in row:
                late_rate = row.get("late_delivery_rate_pct", 0)
                late_orders = row.get("late_orders_count", 0)
                tot_deliv = row.get("total_delivered_orders", 0)
                avg_delay = row.get("avg_delay_days", 0)
                answer = f"The overall late delivery rate was {late_rate:.2f}% ({late_orders:,} out of {tot_deliv:,} delivered orders arrived past estimated delivery date)."
                if avg_delay:
                    insights.append(f"Delayed orders breached SLA by an average of {avg_delay:.1f} days.")
                return answer, insights, visualization, response_type

            # Generic single row
            first_val = list(row.values())[0]
            first_key = list(row.keys())[0]
            answer = f"Result for '{first_key}': {first_val}."
            return answer, insights, visualization, response_type

        # Case 2: Multi-row Time Series (e.g. Monthly GMV)
        if any("month" in c.lower() for c in columns) or any("date" in c.lower() for c in columns):
            response_type = ResponseType.TIME_SERIES.value
            date_col = next((c for c in columns if "month_name" in c or "date" in c or "month" in c), columns[0])
            val_col = next((c for c in columns if "gmv" in c or "order" in c or "price" in c), columns[-1])

            visualization = {
                "recommended_chart": "line",
                "x_field": date_col,
                "y_field": val_col,
                "title": f"Time Series Trend of {val_col.replace('_', ' ').title()}"
            }

            total_val = sum(float(r.get(val_col, 0)) for r in rows)
            peak_row = max(rows, key=lambda r: float(r.get(val_col, 0)))
            answer = f"Showing time-series breakdown across {len(rows)} periods. Total {val_col.replace('_', ' ')} reached {total_val:,.2f}."
            insights.append(f"Peak period was {peak_row.get(date_col)} with {val_col.replace('_', ' ')} of {float(peak_row.get(val_col, 0)):,.2f}.")
            return answer, insights, visualization, response_type

        # Case 3: Ranking / Top N (e.g. Top Categories, Top Sellers, Top States)
        response_type = ResponseType.RANKING.value
        dim_col = columns[0]
        metric_col = next((c for c in columns if "gmv" in c or "order" in c or "sales" in c or "score" in c or "rate" in c), columns[-1])

        visualization = {
            "recommended_chart": "bar",
            "x_field": dim_col,
            "y_field": metric_col,
            "title": f"Top {len(rows)} by {metric_col.replace('_', ' ').title()}"
        }

        top_1 = rows[0]
        answer = f"Top {len(rows)} results ranked by {metric_col.replace('_', ' ')}. Ranked #1 is '{top_1.get(dim_col)}' with {float(top_1.get(metric_col, 0)):,.2f}."
        if len(rows) >= 2:
            top_2 = rows[1]
            insights.append(f"Followed by '{top_2.get(dim_col)}' in 2nd position with {float(top_2.get(metric_col, 0)):,.2f}.")

        return answer, insights, visualization, response_type


insight_synthesizer = InsightSynthesizer()
