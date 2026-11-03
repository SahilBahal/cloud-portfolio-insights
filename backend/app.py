"""Flask API for the Cloud Portfolio Insights dashboard."""

import os

from flask import Flask, g, jsonify, request
from flask_cors import CORS

import analytics
from db import DEFAULT_DB_PATH, get_connection
from seed import build


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("PORTFOLIO_DB", DEFAULT_DB_PATH)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Build the database on first run so the app works straight away
    if not os.path.exists(app.config["DB_PATH"]):
        build(app.config["DB_PATH"])

    def db():
        if "db" not in g:
            g.db = get_connection(app.config["DB_PATH"])
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        conn = g.pop("db", None)
        if conn is not None:
            conn.close()

    def int_arg(name, default, low, high):
        raw = request.args.get(name)
        if raw is None:
            return default
        try:
            value = int(raw)
        except ValueError:
            raise ValueError(f"{name} must be a whole number")
        if not low <= value <= high:
            raise ValueError(f"{name} must be between {low} and {high}")
        return value

    @app.errorhandler(ValueError)
    def bad_request(err):
        return jsonify({"error": str(err)}), 400

    @app.errorhandler(LookupError)
    def not_found(err):
        return jsonify({"error": str(err).strip("'")}), 404

    @app.errorhandler(404)
    def unknown_route(_err):
        return jsonify({"error": "endpoint not found"}), 404

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/services")
    def list_services():
        return jsonify(analytics.services(db()))

    @app.get("/api/summary")
    def summary():
        months = int_arg("months", 12, 2, 18)
        return jsonify(analytics.summary(db(), months))

    @app.get("/api/consumption")
    def consumption():
        group_by = request.args.get("group_by", "service")
        months = int_arg("months", 12, 1, 18)
        return jsonify(analytics.consumption(db(), group_by, months))

    @app.get("/api/pricing")
    def pricing():
        return jsonify(analytics.pricing(db()))

    @app.get("/api/clients/top")
    def top_clients():
        limit = int_arg("limit", 10, 1, 50)
        months = int_arg("months", 12, 1, 18)
        return jsonify(analytics.top_clients(db(), limit, months))

    @app.get("/api/signings")
    def signings():
        months = int_arg("months", 12, 1, 18)
        return jsonify(analytics.signings_vs_revenue(db(), months))

    @app.get("/api/forecast")
    def forecast():
        service_id = request.args.get("service_id")
        if service_id is not None:
            try:
                service_id = int(service_id)
            except ValueError:
                raise ValueError("service_id must be a whole number")
        horizon = int_arg("horizon", 3, 1, 12)
        history = int_arg("history", 12, 3, 18)
        return jsonify(analytics.forecast(db(), service_id, horizon, history))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
