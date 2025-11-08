from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter

# ------------------------
# Date Parsing
# ------------------------
def parse_date_range(text: str, now: datetime):
    """Parse natural language timeframes like today, yesterday, this week, etc."""
    t = text.lower().strip()

    def day_bounds(dt):
        start = datetime(dt.year, dt.month, dt.day, tzinfo=dt.tzinfo)
        end = start + timedelta(days=1) - timedelta(microseconds=1)
        return start, end

    if "today" in t:
        start, end = day_bounds(now)
        return start, end, f"Today ({start.date().isoformat()})"

    if "yesterday" in t:
        y = now - timedelta(days=1)
        start, end = day_bounds(y)
        return start, end, f"Yesterday ({start.date().isoformat()})"

    if "last week" in t:
        this_monday = now - timedelta(days=now.weekday())
        last_monday = this_monday - timedelta(days=7)
        last_sunday = last_monday + timedelta(days=6)
        return last_monday, last_sunday, f"Last week ({last_monday.date()} to {last_sunday.date()})"

    if "this week" in t:
        this_monday = now - timedelta(days=now.weekday())
        return this_monday, now, f"This week ({this_monday.date()} to {now.date()})"

    if "this month" in t:
        start = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)
        nm = datetime(now.year + (now.month // 12), (now.month % 12) + 1, 1, tzinfo=now.tzinfo)
        end = nm - timedelta(microseconds=1)
        return start, end, f"This month ({start.date()} to {end.date()})"

    if "last month" in t:
        if now.month == 1:
            start = datetime(now.year - 1, 12, 1, tzinfo=now.tzinfo)
        else:
            start = datetime(now.year, now.month - 1, 1, tzinfo=now.tzinfo)
        end = datetime(now.year, now.month, 1, tzinfo=now.tzinfo) - timedelta(microseconds=1)
        return start, end, f"Last month ({start.date()} to {end.date()})"

    # Default to today
    start, end = day_bounds(now)
    return start, end, f"Today ({start.date().isoformat()})"


# ------------------------
# Helpers
# ------------------------
def friendly_currency(cents: int) -> str:
    """Convert cents to a readable dollar format."""
    return f"${(cents or 0)/100:.2f}"


# ------------------------
# Aggregation Logic
# ------------------------
def aggregate_metrics(orders, start_dt, end_dt):
    """
    Aggregates both recorded and calculated revenue, AOV, top items, and daily trends.
    Uses hybrid approach to ensure accurate revenue even if 'total' is missing in some orders.
    """

    order_count = len(orders)
    total_revenue_cents = 0        # From order.total
    calc_revenue_cents = 0         # From line items
    item_counter = Counter()
    item_revenue = Counter()
    trend_daily = defaultdict(lambda: [0, 0])  # {date: [revenue, order_count]}

    for o in orders:
        # Get values safely
        order_total = int(o.get("total") or 0)
        line_total = sum(int(i.get("price") or 0) for i in o.get("lineItems", []))
        created_date = o.get("createdTime", "")[:10]

        # Recorded revenue (from order totals)
        total_revenue_cents += order_total

        # Calculated revenue (from line items)
        calc_revenue_cents += line_total

        # Use whichever is valid for daily trend visualization
        trend_daily[created_date][0] += order_total if order_total > 0 else line_total
        trend_daily[created_date][1] += 1

        # Count item stats
        for li in o.get("lineItems", []) or []:
            name = li.get("name") or "Unknown Item"
            qty = li.get("unitQty") if li.get("unitQty") else 1
            price = int(li.get("price") or 0)
            item_counter[name] += qty
            item_revenue[name] += price * qty

    # Top items
    top_items = [
        {"name": n, "qty": int(q), "revenue_cents": int(item_revenue[n])}
        for n, q in item_counter.most_common(10)
    ]

    # Average Order Value (based on recorded totals)
    aov_cents = int(total_revenue_cents / order_count) if order_count else 0

    # Sort daily trend
    trend_daily = {k: (v[0], v[1]) for k, v in sorted(trend_daily.items())}

    return {
        "order_count": order_count,
        "total_revenue_cents": total_revenue_cents,
        "calc_revenue_cents": calc_revenue_cents,
        "aov_cents": aov_cents,
        "top_items": top_items,
        "trend_daily": trend_daily,
    }


# ------------------------
# Trend Insight
# ------------------------
def analyze_trend(trend_daily):
    """Generate human-readable insight about sales trend."""
    if not trend_daily:
        return "No sales data available for the selected period."

    days = list(trend_daily.keys())
    revenues = [trend_daily[d][0] for d in days]

    if len(revenues) < 2:
        return "Sales appear consistent for the selected period."

    start_rev, end_rev = revenues[0], revenues[-1]
    diff = end_rev - start_rev
    pct = (diff / start_rev * 100) if start_rev > 0 else 0

    max_day = max(trend_daily.items(), key=lambda kv: kv[1][0])[0]
    min_day = min(trend_daily.items(), key=lambda kv: kv[1][0])[0]

    if pct > 10:
        direction = f"Sales increased {pct:.0f}% from {days[0]} to {days[-1]}."
    elif pct < -10:
        direction = f"Sales decreased {abs(pct):.0f}% from {days[0]} to {days[-1]}."
    else:
        direction = "Sales remained fairly steady during this period."

    return f"{direction} {max_day} had the highest revenue, while {min_day} was the lowest."
