"""SQLite connection helpers and schema for the portfolio database."""

import os
import sqlite3

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS services (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    category    TEXT NOT NULL,
    unit        TEXT NOT NULL,
    list_price  REAL NOT NULL          -- our list price per unit, in USD
);

CREATE TABLE IF NOT EXISTS competitor_prices (
    service_id  INTEGER NOT NULL REFERENCES services(id),
    competitor  TEXT NOT NULL,
    price       REAL NOT NULL,
    PRIMARY KEY (service_id, competitor)
);

CREATE TABLE IF NOT EXISTS clients (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    industry  TEXT NOT NULL,
    region    TEXT NOT NULL
);

-- One row per client, per service, per month
CREATE TABLE IF NOT EXISTS usage (
    client_id   INTEGER NOT NULL REFERENCES clients(id),
    service_id  INTEGER NOT NULL REFERENCES services(id),
    month       TEXT NOT NULL,         -- YYYY-MM
    units       REAL NOT NULL,
    PRIMARY KEY (client_id, service_id, month)
);

-- New contract signings (total contract value, booked in the month signed)
CREATE TABLE IF NOT EXISTS signings (
    id          INTEGER PRIMARY KEY,
    client_id   INTEGER NOT NULL REFERENCES clients(id),
    month       TEXT NOT NULL,
    amount      REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_usage_month ON usage(month);
CREATE INDEX IF NOT EXISTS idx_signings_month ON signings(month);
"""


def get_connection(db_path=None):
    conn = sqlite3.connect(db_path or DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()
