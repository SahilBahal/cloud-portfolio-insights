"""Generate a synthetic cloud portfolio dataset.

Everything here is made up. The numbers are random but seeded, so every run
produces the same database, which keeps the tests and screenshots stable.

Run directly to rebuild the database:
    python seed.py
"""

import random

from db import DEFAULT_DB_PATH, get_connection, init_schema

SEED = 42

# name, category, unit, our list price per unit
SERVICES = [
    ("Virtual Servers", "Compute", "vCPU-hour", 0.048),
    ("GPU Instances", "Compute", "GPU-hour", 2.95),
    ("Kubernetes Service", "Containers", "cluster-hour", 0.10),
    ("Object Storage", "Storage", "GB-month", 0.022),
    ("Block Storage", "Storage", "GB-month", 0.10),
    ("Managed PostgreSQL", "Databases", "instance-hour", 0.21),
    ("AI Inference API", "AI", "1K tokens", 0.0020),
    ("Serverless Functions", "Compute", "1M invocations", 0.20),
]

# How each competitor tends to price relative to us (1.0 = same price)
COMPETITORS = {
    "Competitor A": 1.04,
    "Competitor B": 0.96,
    "Competitor C": 1.10,
}

# Where the market sits for each service relative to our price.
# Below 1.0 means competitors are cheaper (we're priced at a premium),
# above 1.0 means they're more expensive (we're the cheaper option).
MARKET_LEVEL = {
    "Virtual Servers": 1.00,
    "GPU Instances": 0.86,
    "Kubernetes Service": 1.02,
    "Object Storage": 1.15,
    "Block Storage": 0.97,
    "Managed PostgreSQL": 0.90,
    "AI Inference API": 1.18,
    "Serverless Functions": 1.01,
}

# Typical monthly units for a mid-sized client, per service
BASE_UNITS = {
    "Virtual Servers": 60_000,
    "GPU Instances": 900,
    "Kubernetes Service": 4_000,
    "Object Storage": 180_000,
    "Block Storage": 30_000,
    "Managed PostgreSQL": 3_000,
    "AI Inference API": 1_500_000,
    "Serverless Functions": 2_000,
}

# Monthly growth rate per service. AI and GPU grow fastest.
GROWTH = {
    "Virtual Servers": 0.010,
    "GPU Instances": 0.060,
    "Kubernetes Service": 0.025,
    "Object Storage": 0.015,
    "Block Storage": 0.008,
    "Managed PostgreSQL": 0.020,
    "AI Inference API": 0.080,
    "Serverless Functions": 0.030,
}

INDUSTRIES = ["Financial Services", "Healthcare", "Retail", "Government", "Media", "Manufacturing"]
REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America"]
CLIENT_PREFIXES = ["Apex", "Northwind", "Bluepeak", "Ironwood", "Silverline", "Crestview",
                   "Harbor", "Summit", "Keystone", "Lumen", "Redstone", "Oakridge",
                   "Brightwater", "Granite", "Evergreen", "Pinnacle", "Clearpath", "Meridian",
                   "Westfield", "Stonebridge", "Riverside", "Highpoint", "Fairmont", "Cobalt"]
CLIENT_SUFFIXES = {
    "Financial Services": ["Bank", "Capital", "Financial"],
    "Healthcare": ["Health", "Medical", "Care"],
    "Retail": ["Retail", "Stores", "Brands"],
    "Government": ["Agency", "County", "Authority"],
    "Media": ["Media", "Studios", "Networks"],
    "Manufacturing": ["Industries", "Manufacturing", "Works"],
}

MONTHS = [f"{y}-{m:02d}" for y in (2025, 2026) for m in range(1, 13)][:18]  # Jan 2025 - Jun 2026


def build(db_path=None):
    rng = random.Random(SEED)
    conn = get_connection(db_path or DEFAULT_DB_PATH)

    for table in ("signings", "usage", "competitor_prices", "clients", "services"):
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    init_schema(conn)

    # Services and competitor prices
    for i, (name, category, unit, price) in enumerate(SERVICES, start=1):
        conn.execute(
            "INSERT INTO services (id, name, category, unit, list_price) VALUES (?, ?, ?, ?, ?)",
            (i, name, category, unit, price),
        )
        for competitor, factor in COMPETITORS.items():
            noisy = price * MARKET_LEVEL[name] * factor * rng.uniform(0.95, 1.05)
            conn.execute(
                "INSERT INTO competitor_prices (service_id, competitor, price) VALUES (?, ?, ?)",
                (i, competitor, round(noisy, 5)),
            )

    # Clients
    clients = []
    for i in range(1, 25):
        industry = rng.choice(INDUSTRIES)
        name = f"{CLIENT_PREFIXES[i - 1]} {rng.choice(CLIENT_SUFFIXES[industry])}"
        region = rng.choice(REGIONS)
        size = rng.choice([0.4, 0.7, 1.0, 1.0, 1.5, 2.5])  # a few large accounts
        start = rng.randint(0, 8)                          # month index they onboarded
        clients.append((i, size, start))
        conn.execute(
            "INSERT INTO clients (id, name, industry, region) VALUES (?, ?, ?, ?)",
            (i, name, industry, region),
        )

    # Monthly usage
    for client_id, size, start in clients:
        adopted = {s[0] for s in SERVICES if rng.random() < 0.7}
        for idx, month in enumerate(MONTHS):
            if idx < start:
                continue
            age = idx - start
            for service_id, (name, *_rest) in enumerate(SERVICES, start=1):
                if name not in adopted:
                    continue
                trend = (1 + GROWTH[name]) ** age
                noise = rng.uniform(0.85, 1.15)
                units = BASE_UNITS[name] * size * trend * noise
                conn.execute(
                    "INSERT INTO usage (client_id, service_id, month, units) VALUES (?, ?, ?, ?)",
                    (client_id, service_id, month, round(units, 2)),
                )

    # Signings: each client signs a few contracts over the period
    for client_id, size, start in clients:
        for _ in range(rng.randint(1, 4)):
            month = MONTHS[rng.randint(start, len(MONTHS) - 1)]
            amount = round(rng.uniform(80_000, 600_000) * size, -3)
            conn.execute(
                "INSERT INTO signings (client_id, month, amount) VALUES (?, ?, ?)",
                (client_id, month, amount),
            )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    build()
    print(f"Seeded database at {DEFAULT_DB_PATH}")
