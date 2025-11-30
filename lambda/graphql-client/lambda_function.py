"""
Lambda Function: GraphQL Client (Updated for FactoryTwin Real API)

Purpose: Executes GraphQL queries against the FactoryTwin API using the
latest schema that relies on the simulation identifier field.
"""

import json
import os
from datetime import datetime, timedelta

import requests

# GraphQL endpoint configuration (override via environment)
GRAPHQL_URL = os.environ.get("GRAPHQL_URL", "http://10.1.10.184:9000/graphql")
SIMULATION_ID = os.environ.get("SIMULATION_ID", "test-simulation")


def generate_period_boundaries():
    """Generate 19 month boundaries from Jan 2025 to Jul 2026."""
    start_date = datetime(2025, 1, 1)
    boundaries = []
    for i in range(19):
        date = start_date + timedelta(days=30 * i)
        boundaries.append(date.strftime("%Y-%m-01T00:00:00Z"))
    return boundaries


def generate_period_boundaries_from_range(from_date_str, until_date_str):
    """Generate period boundaries for histogram based on date range."""
    from_date = datetime.fromisoformat(from_date_str.replace('Z', '+00:00'))
    until_date = datetime.fromisoformat(until_date_str.replace('Z', '+00:00'))
    
    boundaries = []
    current = from_date.replace(day=1)  # Start of month
    
    # Generate monthly boundaries
    while current <= until_date:
        boundaries.append(current.strftime("%Y-%m-%dT00:00:00Z"))
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)
    
    # Ensure until_date is included
    if boundaries and boundaries[-1] != until_date_str:
        # Add until_date as final boundary if it's different
        final_date = datetime.fromisoformat(until_date_str.replace('Z', '+00:00'))
        if final_date > datetime.fromisoformat(boundaries[-1].replace('Z', '+00:00')):
            boundaries.append(until_date_str)
    
    return boundaries


# Hardcoded query templates using "identifier" instead of "id"
QUERY_TEMPLATES = {
    "listSimulations": """
        query ListSimulations {
            simulations {
                identifier
                name
            }
        }
    """,
    "demandByFulfillmentDonut": """
        query DonutQuery($simulationId: UUID!, $from: Instant!, $until: Instant!, $sites: [UUID!]!, $buffer: Float!, $useProjectedCompletion: Boolean) {
            simulation(identifier: $simulationId) {
                charts {
                    demandByFulfillmentDonut(
                        from: $from
                        until: $until
                        sites: $sites
                        onTimeDeliveryBuffer: $buffer
                        useProjectedCompletion: $useProjectedCompletion
                    ) {
                        startDate
                        stackDataList {
                            name
                            value
                            quantity
                        }
                    }
                }
            }
        }
    """,
    "demandByFulfillmentHistogram": """
        query HistogramQuery($simulationId: UUID!, $periodBoundaries: [Instant!]!, $sites: [UUID!]!, $buffer: Float!) {
            simulation(identifier: $simulationId) {
                charts {
                    demandByFulfillmentHistogram(
                        periodBoundaries: $periodBoundaries
                        sites: $sites
                        onTimeDeliveryBuffer: $buffer
                    ) {
                        startDate
                        stackDataList {
                            name
                            quantity
                            value
                        }
                    }
                }
            }
        }
    """,
}


def execute_graphql_query(endpoint_name, date_range=None):
    """
    Execute GraphQL query for the specified endpoint.
    
    Args:
        endpoint_name: Name of the endpoint
        date_range: Optional dict with 'from' and 'until' keys (ISO 8601 format strings)
    """
    query_template = QUERY_TEMPLATES.get(endpoint_name)
    if not query_template:
        raise ValueError(f"Unknown endpoint: {endpoint_name}")

    # Default date range if not provided
    default_from = "2025-01-01T00:00:00Z"
    default_until = "2025-11-27T00:00:00Z"
    
    if date_range and date_range.get('from') and date_range.get('until'):
        from_date = date_range.get('from')
        until_date = date_range.get('until')
        print(f"📅 Using custom date range: {from_date} to {until_date}")
    else:
        from_date = default_from
        until_date = default_until
        print(f"📅 Using default date range: {from_date} to {until_date}")

    if endpoint_name == "listSimulations":
        variables = {}
    elif endpoint_name == "demandByFulfillmentDonut":
        variables = {
            "simulationId": SIMULATION_ID,
            "from": from_date,
            "until": until_date,
            "sites": [],
            "buffer": 0.0,
            "useProjectedCompletion": None,  # Optional parameter, can be omitted
        }
        # Remove None values from variables (GraphQL doesn't need them)
        variables = {k: v for k, v in variables.items() if v is not None}
    elif endpoint_name == "demandByFulfillmentHistogram":
        # Generate period boundaries based on date range
        period_boundaries = generate_period_boundaries_from_range(from_date, until_date)
        print(f"📊 Generated {len(period_boundaries)} period boundaries for histogram")
        variables = {
            "simulationId": SIMULATION_ID,
            "periodBoundaries": period_boundaries,
            "sites": [],
            "buffer": 0.0,
        }
    else:
        variables = {}

    # Remove None values from variables (GraphQL handles optional parameters)
    clean_variables = {k: v for k, v in variables.items() if v is not None}

    payload = {
        "query": query_template,
        "variables": clean_variables,
    }

    print(f"Executing GraphQL query to: {GRAPHQL_URL}")
    print(f"Endpoint: {endpoint_name}")
    print(f"Simulation ID: {SIMULATION_ID}")
    print(f"Variables: {json.dumps(variables, indent=2)}")

    try:
        headers = {"Content-Type": "application/json"}
        
        # Add authentication if available
        auth_token = os.environ.get("AUTH_TOKEN")
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        response = requests.post(
            GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )
        print(f"Response status code: {response.status_code}")
        
        # Get response text for debugging
        response_text = response.text
        print(f"Response text: {response_text[:500]}")
        
        if response.status_code != 200:
            print(f"Error response: {response_text}")
            raise Exception(f"GraphQL API returned {response.status_code}: {response_text[:200]}")
        
        response.raise_for_status()

        result = response.json()
        if "errors" in result:
            print(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
            raise Exception(f"GraphQL errors: {result['errors']}")

        data = result.get("data", {})
        
        # Handle listSimulations query differently
        if endpoint_name == "listSimulations":
            simulations = data.get("simulations", [])
            if not simulations:
                raise Exception("No simulations found")
            return {
                "statusCode": 200,
                "endpoint": endpoint_name,
                "data": simulations,
            }
        
        simulation = data.get("simulation", {})
        charts = simulation.get("charts", {})
        endpoint_data = charts.get(endpoint_name)

        if not endpoint_data:
            print(f"No data returned. Full response: {json.dumps(result, indent=2)}")
            raise Exception(f"No data returned for endpoint: {endpoint_name}")

        # Handle optional fields - ensure stackDataList exists
        if isinstance(endpoint_data, dict) and "stackDataList" in endpoint_data:
            # Validate stackDataList structure
            stack_data = endpoint_data.get("stackDataList", [])
            if not isinstance(stack_data, list):
                print(f"Warning: stackDataList is not a list: {type(stack_data)}")
            else:
                print(f"Successfully retrieved {len(stack_data)} items in stackDataList")

        print(f"Successfully retrieved data from {endpoint_name}")
        print(f"Data structure: {json.dumps(endpoint_data, indent=2)[:500]}...")
        return {
            "statusCode": 200,
            "endpoint": endpoint_name,
            "data": endpoint_data,
        }

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        raise Exception(f"Failed to connect to GraphQL API: {str(e)}")
    except Exception as e:
        print(f"Error executing GraphQL query: {e}")
        import traceback

        traceback.print_exc()
        raise


def lambda_handler(event, context):
    """AWS Lambda handler function."""
    print(f"Received event: {json.dumps(event)}")
    try:
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)

        endpoint_name = body.get("endpoint", "")
        if not endpoint_name:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "No endpoint specified", "message": "Please provide an 'endpoint' field"}
                ),
            }

        result = execute_graphql_query(endpoint_name)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "endpoint": result["endpoint"],
                    "data": result["data"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
        }
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(e),
                    "message": "Error executing GraphQL query",
                }
            ),
        }


if __name__ == "__main__":
    test_endpoints = [
        "demandByFulfillmentDonut",
        "demandByFulfillmentHistogram",
    ]
    for endpoint in test_endpoints:
        print("\n" + "=" * 60)
        print(f"Testing endpoint: {endpoint}")
        event = {"body": json.dumps({"endpoint": endpoint})}
        result = lambda_handler(event, {})
        if result["statusCode"] == 200:
            body = json.loads(result["body"])
            print("Success! Data sample:")
            print(json.dumps(body["data"], indent=2)[:500] + "...")
        else:
            print(f"Error: {result['body']}")

