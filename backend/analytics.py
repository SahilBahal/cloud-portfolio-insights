"""Portfolio analytics queries.

Each function takes an open SQLite connection and returns plain Python
data (lists and dicts) that the API turns straight into JSON. Revenue is
always computed as units consumed x our list price.
"""

GROUP_COLUMNS = {
    "service": "s.name",
    "category": "s.category",
    "industry": "c.industry",
    "region": "c.region",
}


def _months(conn):
    return [r["month"] for r in conn.execute("SELECT DISTINCT month FROM usage ORDER BY month")]


def _window(conn, months):
    """Return the last `months` months in the data, oldest first."""
    all_months = _months(conn)
    return all_months[-months:] if months else all_months


def _pct_change(new, old):
    if not old:
        return None
    return round((new - old) / old * 100, 1) + 0.0  # + 0.0 turns -0.0 into 0.0


def summary(conn, months=12):
    window = _window(conn, months)
    placeholders = ",".join("?" * len(window))

    monthly = conn.execute(
        f"""
        SELECT u.month, SUM(u.units * s.list_price) AS revenue
        FROM usage u JOIN services s ON s.id = u.service_id
        WHERE u.month IN ({placeholders})
        GROUP BY u.month ORDER BY u.month
        """,
        window,
    ).fetchall()
    revenue_by_month = [r["revenue"] for r in monthly]

    total_revenue = sum(revenue_by_month)
    latest = revenue_by_month[-1] if revenue_by_month else 0
    previous = revenue_by_month[-2] if len(revenue_by_month) > 1 else 0

    active_clients = conn.execute(
        "SELECT COUNT(DISTINCT client_id) AS n FROM usage WHERE month = ?", (window[-1],)
    ).fetchone()["n"]

    total_signings = conn.execute(
        f"SELECT COALESCE(SUM(amount), 0) AS total FROM signings WHERE month IN ({placeholders})",
        window,
    ).fetchone()["total"]

    top = conn.execute(
        f"""
        SELECT s.name, SUM(u.units * s.list_price) AS revenue
        FROM usage u JOIN services s ON s.id = u.service_id
        WHERE u.month IN ({placeholders})
        GROUP BY s.name ORDER BY revenue DESC LIMIT 1
        """,
        window,
    ).fetchone()

    return {
        "period_start": window[0],
        "period_end": window[-1],
        "total_revenue": round(total_revenue, 2),
        "latest_month_revenue": round(latest, 2),
        "mom_growth_pct": _pct_change(latest, previous),
        "active_clients": active_clients,
        "total_signings": round(total_signings, 2),
        "top_service": top["name"] if top else None,
    }


def consumption(conn, group_by="service", months=12):
    if group_by not in GROUP_COLUMNS:
        raise ValueError(f"group_by must be one of: {', '.join(GROUP_COLUMNS)}")
    window = _window(conn, months)
    placeholders = ",".join("?" * len(window))
    col = GROUP_COLUMNS[group_by]

    rows = conn.execute(
        f"""
        SELECT u.month, {col} AS grp, SUM(u.units * s.list_price) AS revenue
        FROM usage u
        JOIN services s ON s.id = u.service_id
        JOIN clients c  ON c.id = u.client_id
        WHERE u.month IN ({placeholders})
        GROUP BY u.month, grp
        ORDER BY u.month
        """,
        window,
    ).fetchall()

    groups = sorted({r["grp"] for r in rows})
    table = {m: {g: 0.0 for g in groups} for m in window}
    for r in rows:
        table[r["month"]][r["grp"]] = round(r["revenue"], 2)

    return {
        "group_by": group_by,
        "groups": groups,
        "series": [{"month": m, **table[m]} for m in window],
    }


def pricing(conn):
    rows = conn.execute(
        """
        SELECT s.id, s.name, s.category, s.unit, s.list_price,
               AVG(cp.price) AS competitor_avg,
               MIN(cp.price) AS competitor_min
        FROM services s JOIN competitor_prices cp ON cp.service_id = s.id
        GROUP BY s.id ORDER BY s.name
        """
    ).fetchall()

    result = []
    for r in rows:
        gap = _pct_change(r["list_price"], r["competitor_avg"])
        if gap is None:
            position = "unknown"
        elif gap > 5:
            position = "premium"
        elif gap < -5:
            position = "discount"
        else:
            position = "at market"
        result.append({
            "service_id": r["id"],
            "service": r["name"],
            "category": r["category"],
            "unit": r["unit"],
            "our_price": r["list_price"],
            "competitor_avg": round(r["competitor_avg"], 5),
            "competitor_min": round(r["competitor_min"], 5),
            "gap_vs_avg_pct": gap,
            "position": position,
        })
    return result


def top_clients(conn, limit=10, months=12):
    window = _window(conn, months)
    placeholders = ",".join("?" * len(window))
    rows = conn.execute(
        f"""
        SELECT c.id, c.name, c.industry, c.region,
               SUM(u.units * s.list_price) AS revenue,
               COUNT(DISTINCT u.service_id) AS services_used
        FROM usage u
        JOIN services s ON s.id = u.service_id
        JOIN clients c  ON c.id = u.client_id
        WHERE u.month IN ({placeholders})
        GROUP BY c.id ORDER BY revenue DESC LIMIT ?
        """,
        [*window, limit],
    ).fetchall()
    return [
        {
            "client_id": r["id"],
            "name": r["name"],
            "industry": r["industry"],
            "region": r["region"],
            "revenue": round(r["revenue"], 2),
            "services_used": r["services_used"],
        }
        for r in rows
    ]


def signings_vs_revenue(conn, months=12):
    window = _window(conn, months)
    placeholders = ",".join("?" * len(window))
    revenue = {
        r["month"]: r["v"]
        for r in conn.execute(
            f"""SELECT u.month, SUM(u.units * s.list_price) AS v
                FROM usage u JOIN services s ON s.id = u.service_id
                WHERE u.month IN ({placeholders}) GROUP BY u.month""",
            window,
        )
    }
    signings = {
        r["month"]: r["v"]
        for r in conn.execute(
            f"SELECT month, SUM(amount) AS v FROM signings WHERE month IN ({placeholders}) GROUP BY month",
            window,
        )
    }
    return [
        {"month": m, "revenue": round(revenue.get(m, 0), 2), "signings": round(signings.get(m, 0), 2)}
        for m in window
    ]


def _linear_fit(ys):
    """Ordinary least squares on (0..n-1, ys). Returns slope, intercept."""
    n = len(ys)
    xs = range(n)
    x_mean = (n - 1) / 2
    y_mean = sum(ys) / n
    sxx = sum((x - x_mean) ** 2 for x in xs)
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    slope = sxy / sxx if sxx else 0.0
    return slope, y_mean - slope * x_mean


def _next_month(month, step):
    year, mon = map(int, month.split("-"))
    total = year * 12 + (mon - 1) + step
    return f"{total // 12}-{total % 12 + 1:02d}"


def forecast(conn, service_id=None, horizon=3, history=12):
    """Project monthly revenue forward with a simple linear trend.

    This is a baseline, not a serious forecasting model. It's useful for a
    quick read on direction, and the history it returns lets you see how
    well a straight line actually fits.
    """
    if horizon < 1 or horizon > 12:
        raise ValueError("horizon must be between 1 and 12")

    window = _window(conn, history)
    placeholders = ",".join("?" * len(window))
    params = list(window)
    service_filter = ""
    service_name = "All services"

    if service_id is not None:
        row = conn.execute("SELECT name FROM services WHERE id = ?", (service_id,)).fetchone()
        if row is None:
            raise LookupError(f"service {service_id} not found")
        service_name = row["name"]
        service_filter = "AND s.id = ?"
        params.append(service_id)

    rows = conn.execute(
        f"""
        SELECT u.month, SUM(u.units * s.list_price) AS revenue
        FROM usage u JOIN services s ON s.id = u.service_id
        WHERE u.month IN ({placeholders}) {service_filter}
        GROUP BY u.month ORDER BY u.month
        """,
        params,
    ).fetchall()

    actual = [r["revenue"] for r in rows]
    slope, intercept = _linear_fit(actual)
    n = len(actual)

    history_points = [
        {"month": r["month"], "actual": round(r["revenue"], 2), "fitted": round(intercept + slope * i, 2)}
        for i, r in enumerate(rows)
    ]
    projected = [
        {"month": _next_month(rows[-1]["month"], k), "forecast": round(max(intercept + slope * (n - 1 + k), 0), 2)}
        for k in range(1, horizon + 1)
    ]

    return {
        "service": service_name,
        "monthly_trend": round(slope, 2),
        "history": history_points,
        "forecast": projected,
    }


def services(conn):
    return [dict(r) for r in conn.execute("SELECT id, name, category, unit FROM services ORDER BY name")]
