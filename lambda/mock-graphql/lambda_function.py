"""
AWS Lambda mock GraphQL endpoint used for integration testing.
Returns deterministic data for the FactoryTwin donut + histogram charts.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

from decimal import Decimal

DONUT_DATA = {
    "startDate": "2025-01-01T00:00:00Z",
    "stackDataList": [
        {"name": "Overdue", "quantity": 149, "value": 1079098.66},
        {"name": "Forecasted", "quantity": 2316, "value": 14611009.21},
        {"name": "Firm Order", "quantity": 4848, "value": 32595400.38},
    ],
}


def _month_start(start: datetime, offset: int) -> datetime:
    year = start.year + (start.month - 1 + offset) // 12
    month = (start.month - 1 + offset) % 12 + 1
    return datetime(year, month, 1, tzinfo=start.tzinfo)


def generate_histogram_data() -> List[Dict[str, Any]]:
    start_date = datetime(2025, 1, 1)
    data: List[Dict[str, Any]] = []
    for i in range(19):
        month_date = _month_start(start_date, i)
        base_value = 2_000_000 + (i * 75_000)
        data.append(
            {
                "startDate": month_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "stackDataList": [
                    {
                        "name": "Overdue",
                        "quantity": 120 + (i % 40),
                        "value": round(base_value * 0.12 + i * 10_000, 2),
                    },
                    {
                        "name": "Forecasted",
                        "quantity": 2000 + (i * 25),
                        "value": round(base_value * 0.3 + i * 25_000, 2),
                    },
                    {
                        "name": "Firm Order",
                        "quantity": 3800 + (i * 35),
                        "value": round(base_value * 0.58 + i * 55_000, 2),
                    },
                ],
            }
        )
    return data


HISTOGRAM_DATA = generate_histogram_data()


def resolve_query(query: str) -> Dict[str, Any]:
    if "demandByFulfillmentDonut" in query:
        return {
            "simulation": {"charts": {"demandByFulfillmentDonut": DONUT_DATA}},
        }
    if "demandByFulfillmentHistogram" in query:
        return {
            "simulation": {"charts": {"demandByFulfillmentHistogram": HISTOGRAM_DATA}},
        }
    return {"simulation": {"charts": {}}}


def lambda_handler(event, context):
    try:
        raw_body = event.get("body") or "{}"
        if isinstance(raw_body, str):
            body = json.loads(raw_body)
        else:
            body = raw_body

        query = body.get("query", "")
        response_data = resolve_query(query)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"data": response_data}),
        }
    except Exception as exc:  # pragma: no cover - defensive logging
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc)}),
        }

