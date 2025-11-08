
# import os
# import json
# from datetime import datetime, timedelta, timezone
# from flask import Flask, render_template, request, jsonify
# from sales_api import fetch_recent_orders
# from llm_agent import llm_explain
# from utils import parse_date_range, aggregate_metrics, friendly_currency, analyze_trend

# app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def index():
#     return render_template("index.html")

# @app.route("/ask", methods=["POST"])
# def ask():
#     try:
#         q = (request.form.get("question") or request.json.get("question") or "").strip()
#         if not q:
#             return jsonify({"error": "Please provide a question."}), 400

#         tz = timezone.utc
#         start_dt, end_dt, range_label = parse_date_range(q, now=datetime.now(tz))

#         # Fetch orders
#         orders = fetch_recent_orders()

#         def in_range(o):
#             try:
#                 ct = datetime.fromisoformat(o["createdTime"])
#             except Exception:
#                 return False
#             ct = ct.replace(tzinfo=None)
#             return start_dt.replace(tzinfo=None) <= ct <= end_dt.replace(tzinfo=None) and o.get("state") == "locked"

#         filtered = [o for o in orders if in_range(o)]
#         metrics = aggregate_metrics(filtered, start_dt, end_dt)
#         trend_insight = analyze_trend(metrics["trend_daily"])

#         analysis = {
#             "question": q,
#             "date_range": {"start": start_dt.isoformat(), "end": end_dt.isoformat(), "label": range_label},
#             "totals": {
#                 "revenue_cents": metrics["total_revenue_cents"],
#                 "calc_revenue_cents": metrics["calc_revenue_cents"],
#                 "orders": metrics["order_count"],
#                 "avg_order_value_cents": metrics["aov_cents"],
#             },
#             "top_items": metrics["top_items"],
#             "trend": metrics["trend_daily"],
#             "trend_insight": trend_insight,
#         }

#         llm_answer = llm_explain(analysis)

#         # Detect what to display
#         q_lower = q.lower()
#         show_top = any(k in q_lower for k in ["top", "best", "selling", "item", "product"])
#         show_revenue = any(k in q_lower for k in ["revenue", "income", "sales total"])
#         show_trend = any(k in q_lower for k in ["trend", "compare", "growth", "week", "day", "month"])
#         show_general = not (show_top or show_revenue or show_trend)

#         ui = {
#             "label": range_label,
#             "llm_answer": llm_answer,
#             "show_top": show_top,
#             "show_revenue": show_revenue,
#             "show_trend": show_trend,
#             "show_general": show_general,
#             "orders": metrics["order_count"],
#             "revenue": friendly_currency(metrics["total_revenue_cents"]),
#             "calc_revenue": friendly_currency(metrics["calc_revenue_cents"]),
#             "aov": friendly_currency(metrics["aov_cents"]),
#             "trend_insight": trend_insight,
#             "top_items": [
#                 {"name": i["name"], "qty": i["qty"], "revenue": friendly_currency(i["revenue_cents"])}
#                 for i in metrics["top_items"]
#             ],
#             "trend": [{"date": d, "revenue": round(v / 100.0, 2), "orders": c} for d, (v, c) in metrics["trend_daily"].items()],
#         }

#         return jsonify(ui)

#     except Exception as e:
#         return jsonify({"error": f"Something went wrong: {str(e)}"}), 500


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port, debug=True)



import os
import json
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, jsonify, session
from sales_api import fetch_recent_orders
from llm_agent import llm_explain
from utils import parse_date_range, aggregate_metrics, friendly_currency, analyze_trend

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")  # for session handling

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        q = (request.form.get("question") or request.json.get("question") or "").strip()
        if not q:
            return jsonify({"error": "Please provide a question."}), 400

        # Retrieve conversation context
        convo = session.get("conversation_history", [])

        tz = timezone.utc
        start_dt, end_dt, range_label = parse_date_range(q, now=datetime.now(tz))

        orders = fetch_recent_orders()

        def in_range(o):
            try:
                ct = datetime.fromisoformat(o["createdTime"])
            except Exception:
                return False
            ct = ct.replace(tzinfo=None)
            return start_dt.replace(tzinfo=None) <= ct <= end_dt.replace(tzinfo=None) and o.get("state") == "locked"

        filtered = [o for o in orders if in_range(o)]
        metrics = aggregate_metrics(filtered, start_dt, end_dt)
        trend_insight = analyze_trend(metrics["trend_daily"])

        analysis = {
            "question": q,
            "date_range": {"start": start_dt.isoformat(), "end": end_dt.isoformat(), "label": range_label},
            "totals": {
                "revenue_cents": metrics["total_revenue_cents"],
                "calc_revenue_cents": metrics["calc_revenue_cents"],
                "orders": metrics["order_count"],
                "avg_order_value_cents": metrics["aov_cents"],
            },
            "top_items": metrics["top_items"],
            "trend": metrics["trend_daily"],
            "trend_insight": trend_insight,
            "conversation_context": convo[-3:],  # include last 3 turns
        }

        llm_answer = llm_explain(analysis)

        # Update conversation memory
        convo.append({"user": q, "bot": llm_answer})
        session["conversation_history"] = convo[-5:]  # keep recent 5

        q_lower = q.lower()
        show_top = any(k in q_lower for k in ["top", "best", "selling", "item", "product"])
        show_revenue = any(k in q_lower for k in ["revenue", "income", "sales total"])
        show_trend = any(k in q_lower for k in ["trend", "compare", "growth", "week", "day", "month"])
        show_general = not (show_top or show_revenue or show_trend)

        ui = {
            "label": range_label,
            "llm_answer": llm_answer,
            "show_top": show_top,
            "show_revenue": show_revenue,
            "show_trend": show_trend,
            "show_general": show_general,
            "orders": metrics["order_count"],
            "revenue": friendly_currency(metrics["total_revenue_cents"]),
            "calc_revenue": friendly_currency(metrics["calc_revenue_cents"]),
            "aov": friendly_currency(metrics["aov_cents"]),
            "trend_insight": trend_insight,
            "top_items": [
                {"name": i["name"], "qty": i["qty"], "revenue": friendly_currency(i["revenue_cents"])}
                for i in metrics["top_items"]
            ],
            "trend": [{"date": d, "revenue": round(v / 100.0, 2), "orders": c} for d, (v, c) in metrics["trend_daily"].items()],
        }

        return jsonify(ui)

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
