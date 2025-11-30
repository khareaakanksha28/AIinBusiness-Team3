"""
Lambda Function: Intent Classifier

Purpose: Uses Groq LLM to determine which endpoint to call based on user question
"""

import json
import os
import sys

from groq import Groq

MODEL_NAME = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# Initialize Groq client (lazy initialization)
groq_client = None

def get_groq_client():
    """Get or create Groq client"""
    global groq_client
    if groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        groq_client = Groq(api_key=api_key)
    return groq_client

# Endpoint metadata
ENDPOINTS = {
    "demandByFulfillmentDonut": {
        "name": "Total Aggregate Demand",
        "keywords": ["total", "aggregate", "firm order", "revenue", "overdue", "forecasted"],
        "description": "Shows total demand broken down into Firm Orders, Overdue, and Forecasted",
        "visualization": "donut",
    },
    "demandByFulfillmentHistogram": {
        "name": "Monthly Aggregate Demand",
        "keywords": ["monthly", "months", "month", "average", "trend", "over time"],
        "description": "Shows monthly demand over time with breakdown by order type",
        "visualization": "stacked-bar",
    },
}


def classify_intent(user_question):
    """
    Use Groq LLM to classify user intent and determine endpoint
    """

    system_prompt = """You are an AI assistant for FactoryTwin manufacturing software.
Your job is to determine which data endpoint to call based on the user's question AND extract any date ranges mentioned.

CRITICAL: If the user is just saying thank you, goodbye, or acknowledging (not asking for data), respond with:
{"endpoint": "conversational", "extraction_type": "none", "date_range": {"from": null, "until": null}, "confidence": 1.0}

Available endpoints:
1. demandByFulfillmentDonut - Use when user asks about TOTAL or AGGREGATE demand, revenue, or specific order types (firm orders, overdue, forecasted)
2. demandByFulfillmentHistogram - Use when user asks about MONTHLY breakdown, trends over time, or specific months
3. conversational - Use when user is just saying thank you, goodbye, or acknowledging (not asking for data)

IMPORTANT: Extract date ranges from the user's question. If the user mentions specific dates (e.g., "Dec 2025 to May 2026", "from December 25 to May 26"), extract them.

Respond with ONLY a JSON object in this exact format:
{
    "endpoint": "demandByFulfillmentDonut" or "demandByFulfillmentHistogram",
    "extraction_type": "firm_order" or "total" or "overdue" or "forecasted" or "monthly_count" or "average" or "highest_month",
    "date_range": {
        "from": "YYYY-MM-DDTHH:MM:SSZ" or null,
        "until": "YYYY-MM-DDTHH:MM:SSZ" or null
    },
    "confidence": 0.0 to 1.0
}

For date extraction:
- If user says "Dec 2025" or "December 2025", use "2025-12-01T00:00:00Z"
- If user says "May 2026", use "2026-05-01T00:00:00Z"
- If user says "Dec 25 to May 26", interpret as "December 2025 to May 2026"
- If no dates mentioned, set both to null
- Always use ISO 8601 format with Z timezone

Examples:
User: "What is the revenue from my total firm orders?"
Response: {"endpoint": "demandByFulfillmentDonut", "extraction_type": "firm_order", "date_range": {"from": null, "until": null}, "confidence": 0.95}

User: "How many months do I have firm demand?"
Response: {"endpoint": "demandByFulfillmentHistogram", "extraction_type": "monthly_count", "date_range": {"from": null, "until": null}, "confidence": 0.90}

User: "What is my total demand?"
Response: {"endpoint": "demandByFulfillmentDonut", "extraction_type": "total", "date_range": {"from": null, "until": null}, "confidence": 0.95}

User: "What is projected demand from Dec 25 to May 26?"
Response: {"endpoint": "demandByFulfillmentHistogram", "extraction_type": "total", "date_range": {"from": "2025-12-01T00:00:00Z", "until": "2026-05-31T23:59:59Z"}, "confidence": 0.95}

User: "Show me demand from January 2025 to June 2025"
Response: {"endpoint": "demandByFulfillmentHistogram", "extraction_type": "total", "date_range": {"from": "2025-01-01T00:00:00Z", "until": "2025-06-30T23:59:59Z"}, "confidence": 0.95}

User: "Thank you for the information"
Response: {"endpoint": "conversational", "extraction_type": "none", "date_range": {"from": null, "until": null}, "confidence": 1.0}

User: "Thanks, that's all I needed"
Response: {"endpoint": "conversational", "extraction_type": "none", "date_range": {"from": null, "until": null}, "confidence": 1.0}
"""

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
            ],
            temperature=0.2,
            max_tokens=200,
        )

        # Extract response
        llm_response = response.choices[0].message.content.strip()

        # Parse JSON response
        intent_data = json.loads(llm_response)
        
        # Ensure date_range exists in response (for backward compatibility)
        if 'date_range' not in intent_data:
            intent_data['date_range'] = {"from": None, "until": None}

        return {
            "statusCode": 200,
            "intent": intent_data,
            "endpoint_metadata": ENDPOINTS.get(intent_data["endpoint"], {}),
        }

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw LLM response: {llm_response}")

        # Fallback: simple keyword matching
        return fallback_classification(user_question)

    except Exception as e:
        print(f"Groq API error: {e}")
        return fallback_classification(user_question)


def fallback_classification(user_question):
    """
    Simple keyword-based classification as fallback
    """
    question_lower = user_question.lower()

    # Check for monthly/time-based keywords
    if any(word in question_lower for word in ["month", "monthly", "months", "average", "trend"]):
        return {
            "statusCode": 200,
            "intent": {
                "endpoint": "demandByFulfillmentHistogram",
                "extraction_type": "monthly_count",
                "date_range": {"from": None, "until": None},
                "confidence": 0.7,
            },
            "endpoint_metadata": ENDPOINTS["demandByFulfillmentHistogram"],
        }

    # Check for specific order types
    if "firm order" in question_lower or "firm demand" in question_lower:
        extraction = "firm_order"
    elif "overdue" in question_lower:
        extraction = "overdue"
    elif "forecasted" in question_lower or "forecast" in question_lower:
        extraction = "forecasted"
    else:
        extraction = "total"

    # Default to donut chart for aggregate queries
    return {
        "statusCode": 200,
        "intent": {
            "endpoint": "demandByFulfillmentDonut",
            "extraction_type": extraction,
            "date_range": {"from": None, "until": None},
            "confidence": 0.7,
        },
        "endpoint_metadata": ENDPOINTS["demandByFulfillmentDonut"],
    }


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    print(f"Received event: {json.dumps(event)}")

    try:
        # Parse request body
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)

        user_question = body.get("question", "")

        if not user_question:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "No question provided", "message": "Please provide a 'question' field"}
                ),
            }

        # Classify intent
        result = classify_intent(user_question)

        print(f"Classification result: {json.dumps(result)}")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "question": user_question,
                    "intent": result["intent"],
                    "endpoint": result["intent"]["endpoint"],
                    "extraction_type": result["intent"]["extraction_type"],
                    "visualization": result["endpoint_metadata"].get("visualization"),
                    "confidence": result["intent"]["confidence"],
                }
            ),
        }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": str(e), "message": "Internal server error during intent classification"}
            ),
        }


# For local testing
if __name__ == "__main__":
    # Test cases
    test_questions = [
        "What is the revenue from my total firm orders?",
        "How many months do I have firm demand?",
        "What is my average revenue per month?",
        "Show me my overdue orders",
        "What is my total demand?",
    ]

    # Set environment variable for testing
    # IMPORTANT: Set your GROQ_API_KEY environment variable before running
    # Do not hardcode API keys in production code!
    if not os.environ.get("GROQ_API_KEY"):
        print("⚠️  WARNING: GROQ_API_KEY not set. Set it via environment variable.")
        print("   Example: export GROQ_API_KEY='your-key-here'")
        sys.exit(1)

    for question in test_questions:
        print(f"\n{'=' * 60}")
        print(f"Question: {question}")

        event = {"body": json.dumps({"question": question})}

        result = lambda_handler(event, {})
        print(f"Result: {json.dumps(json.loads(result['body']), indent=2)}")

