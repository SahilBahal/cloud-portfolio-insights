import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}


def test_summary_has_kpis(client):
    data = client.get("/api/summary?months=6").get_json()
    assert data["total_revenue"] > 0
    assert data["active_clients"] > 0
    assert data["top_service"]
    assert data["period_end"] == "2026-06"


def test_consumption_groups_and_months(client):
    data = client.get("/api/consumption?group_by=region&months=6").get_json()
    assert len(data["series"]) == 6
    for row in data["series"]:
        assert set(data["groups"]).issubset(row.keys())


def test_consumption_rejects_bad_group(client):
    res = client.get("/api/consumption?group_by=planet")
    assert res.status_code == 400
    assert "group_by" in res.get_json()["error"]


def test_consumption_totals_match_summary(client):
    summary = client.get("/api/summary?months=12").get_json()
    data = client.get("/api/consumption?group_by=service&months=12").get_json()
    total = sum(v for row in data["series"] for k, v in row.items() if k != "month")
    assert total == pytest.approx(summary["total_revenue"], rel=1e-6)


def test_pricing_positions(client):
    rows = client.get("/api/pricing").get_json()
    assert len(rows) == 8
    assert {r["position"] for r in rows} <= {"premium", "discount", "at market"}


def test_top_clients_sorted(client):
    rows = client.get("/api/clients/top?limit=5").get_json()
    assert len(rows) == 5
    revenues = [r["revenue"] for r in rows]
    assert revenues == sorted(revenues, reverse=True)


def test_forecast_horizon(client):
    data = client.get("/api/forecast?service_id=1&horizon=4").get_json()
    assert len(data["forecast"]) == 4
    assert data["forecast"][0]["month"] == "2026-07"


def test_forecast_unknown_service(client):
    res = client.get("/api/forecast?service_id=999")
    assert res.status_code == 404


def test_invalid_number_param(client):
    res = client.get("/api/summary?months=abc")
    assert res.status_code == 400
