import os
import json

def _fallback_explanation(analysis: dict) -> str:
    """Fallback summary when Gemini API is unavailable."""
    q = analysis.get("question", "").lower()
    totals = analysis["totals"]
    label = analysis["date_range"]["label"]
    rev = totals["revenue_cents"] / 100.0
    aov = totals["avg_order_value_cents"] / 100.0 if totals["avg_order_value_cents"] else 0.0

    lines = []

    # --- Detect intent ---
    is_top = any(w in q for w in ["top", "best", "product", "item"])
    is_trend = any(w in q for w in ["trend", "growth", "increase", "decrease", "pattern"])
    is_compare = any(w in q for w in ["compare", "versus", "vs", "difference", "improve"])
    is_summary = not (is_top or is_trend or is_compare)

    # --- Handle comparisons (this week vs last week, today vs yesterday) ---
    if is_compare:
        lines.append(f"Here's the comparison summary for {label}:")
        comp = analysis.get("comparison", {})
        if not comp:
            lines.append("No comparison data available for the requested periods.")
        else:
            rev1, rev2 = comp.get("rev_current", 0), comp.get("rev_previous", 0)
            ord1, ord2 = comp.get("orders_current", 0), comp.get("orders_previous", 0)
            growth_rev = comp.get("rev_growth_pct", 0)
            growth_ord = comp.get("order_growth_pct", 0)

            lines.append(f"Current period revenue: ${rev1:,.2f}")
            lines.append(f"Previous period revenue: ${rev2:,.2f}")
            lines.append(f"Revenue change: {growth_rev:+.1f}%")
            lines.append(f"Orders change: {growth_ord:+.1f}%")

            if growth_rev > 0:
                lines.append("\nSales performance improved compared to the previous period.")
            elif growth_rev < 0:
                lines.append("\nSales performance declined compared to the previous period.")
            else:
                lines.append("\nSales performance remained flat.")

    # --- Top 5 products ---
    elif is_top:
        lines.append(f"Here's what I found for {label}:")
        top_items = analysis.get("top_items", [])
        if not top_items:
            lines.append("No product sales data found for this period.")
        else:
            lines.append("Top 5 best-selling products:")
            for i, item in enumerate(top_items[:5], start=1):
                name = item.get("name", "Unnamed Item")
                qty = item.get("qty", 0)
                revenue = item.get("revenue_cents", 0) / 100.0
                lines.append(f"{i}. {name} — {qty} sold (${revenue:,.2f})")

    # --- Trend-based requests ---
    elif is_trend:
        lines.append(f"Here's the sales trend for {label}:")
        trend = analysis.get("trend", {})
        if not trend:
            lines.append("No trend data available.")
        else:
            for date, (rev_cents, orders) in trend.items():
                lines.append(f"• {date}: ${rev_cents/100:.2f} ({orders} orders)")
        if analysis.get("trend_insight"):
            lines.append(f"\nTrend insight: {analysis['trend_insight']}")

    # --- General summary ---
    else:
        lines.append(f"Here's what I found for {label}:")
        lines.append(f"- Orders: {totals['orders']}")
        lines.append(f"- Revenue: ${rev:,.2f}")
        lines.append(f"- Average order value: ${aov:,.2f}")

        top_items = analysis.get("top_items", [])
        if top_items:
            lines.append("\nTop items:")
            for i, item in enumerate(top_items[:3], start=1):
                name = item.get("name", "Unnamed Item")
                qty = item.get("qty", 0)
                revenue = item.get("revenue_cents", 0) / 100.0
                lines.append(f"{i}. {name} — {qty} sold (${revenue:,.2f})")

        if analysis.get("trend_insight"):
            lines.append(f"\nTrend insight: {analysis['trend_insight']}")

    return "\n".join(lines)


def llm_explain(analysis: dict) -> str:
    """Gemini-powered natural language explanation."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return _fallback_explanation(analysis)

    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)

        q = analysis.get("question", "").lower()
        is_top = any(w in q for w in ["top", "best", "product", "item"])
        is_trend = any(w in q for w in ["trend", "growth", "increase", "decrease", "pattern"])
        is_compare = any(w in q for w in ["compare", "versus", "vs", "difference", "improve"])
        is_summary = not (is_top or is_trend or is_compare)

        system = (
            "You are a professional sales analyst. "
            "Always stay factual. "
            "Summarize or compare sales metrics precisely. "
            "If the question asks for comparison, describe differences in percentages and state whether performance improved or declined. "
            "For 'top' or 'best-selling' questions, list top 5 products. "
            "For 'trend' or 'growth', explain daily changes clearly. "
            "For totals, summarize overall orders, revenue, and AOV."
        )

        prompt = f"""
User Question: {analysis['question']}

Date Range: {analysis['date_range']['label']} ({analysis['date_range']['start']} → {analysis['date_range']['end']})

Totals: {json.dumps(analysis['totals'])}

Top Items: {json.dumps(analysis['top_items'][:10])}

Trend (daily revenue & orders): {json.dumps(analysis['trend'])}

Comparison: {json.dumps(analysis.get('comparison', {}))}

Now provide a clear, concise, data-based answer suitable for a business report.
"""

        model = genai.GenerativeModel("gemini-2.5-pro")
        resp = model.generate_content([system, prompt])
        return resp.text.strip() if hasattr(resp, "text") else str(resp)

    except Exception as e:
        return _fallback_explanation(analysis) + f"\n\n(Note: LLM fallback due to: {e})"
