"""
Lambda Function: Orchestrator

Purpose: Chains together Intent Classifier → GraphQL Client → Response Generator

This is the main entry point that frontend will call
"""

import json

import boto3

import os


# Initialize Lambda client
lambda_client = boto3.client('lambda')


# Lambda function names
INTENT_CLASSIFIER_FUNCTION = "FactoryTwin-IntentClassifier"

GRAPHQL_CLIENT_FUNCTION = "FactoryTwin-GraphQLClient"

RESPONSE_GENERATOR_FUNCTION = "FactoryTwin-ResponseGenerator"




def invoke_lambda(function_name, payload):
    """
    Invoke another Lambda function synchronously
    """
    print(f"Invoking Lambda: {function_name}")
    print(f"Payload: {json.dumps(payload)[:200]}...")
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        
        print(f"Response from {function_name}: {response_payload.get('statusCode')}")
        
        return response_payload
        
    except Exception as e:
        print(f"Error invoking {function_name}: {str(e)}")
        raise




def lambda_handler(event, context):
    """
    Main orchestrator that chains all 3 Lambda functions
    
    Flow:
    1. Receive user question
    2. Call Intent Classifier → get endpoint + extraction_type
    3. Call GraphQL Client → get data from FactoryTwin API
    4. Call Response Generator → get natural language answer + chart data
    5. Return complete response to frontend
    """
    
    print(f"Orchestrator received event: {json.dumps(event)}")
    
    try:
        # Parse incoming request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        user_question = body.get('question', '')
        
        if not user_question:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({
                    "error": "Missing question",
                    "message": "Please provide a 'question' field"
                })
            }
        
        print(f"Processing question: {user_question}")
        
        # ============================================================
        # STEP 1: Classify Intent
        # ============================================================
        print("\n" + "="*60)
        print("STEP 1: Intent Classification")
        print("="*60)
        
        intent_response = invoke_lambda(
            INTENT_CLASSIFIER_FUNCTION,
            {"body": json.dumps({"question": user_question})}
        )
        
        if intent_response.get('statusCode') != 200:
            raise Exception(f"Intent classification failed: {intent_response}")
        
        intent_body = json.loads(intent_response['body'])
        endpoint = intent_body['endpoint']
        extraction_type = intent_body['extraction_type']
        confidence = intent_body.get('confidence', 0)
        
        print(f"✅ Intent: {endpoint}")
        print(f"✅ Extraction: {extraction_type}")
        print(f"✅ Confidence: {confidence}")
        
        # ============================================================
        # STEP 2: Query GraphQL
        # ============================================================
        print("\n" + "="*60)
        print("STEP 2: GraphQL Query")
        print("="*60)
        
        graphql_response = invoke_lambda(
            GRAPHQL_CLIENT_FUNCTION,
            {"body": json.dumps({"endpoint": endpoint})}
        )
        
        if graphql_response.get('statusCode') != 200:
            raise Exception(f"GraphQL query failed: {graphql_response}")
        
        graphql_body = json.loads(graphql_response['body'])
        graphql_data = graphql_body['data']
        
        print(f"✅ Data retrieved from {endpoint}")
        
        # ============================================================
        # STEP 3: Generate Response
        # ============================================================
        print("\n" + "="*60)
        print("STEP 3: Response Generation")
        print("="*60)
        
        response_response = invoke_lambda(
            RESPONSE_GENERATOR_FUNCTION,
            {
                "body": json.dumps({
                    "question": user_question,
                    "graphql_data": graphql_data,
                    "endpoint": endpoint,
                    "extraction_type": extraction_type
                })
            }
        )
        
        if response_response.get('statusCode') != 200:
            raise Exception(f"Response generation failed: {response_response}")
        
        response_body = json.loads(response_response['body'])
        
        print(f"✅ Response generated")
        print(f"Answer: {response_body['response'][:100]}...")
        
        # ============================================================
        # STEP 4: Return Complete Response
        # ============================================================
        print("\n" + "="*60)
        print("STEP 4: Returning Complete Response")
        print("="*60)
        
        final_response = {
            "question": user_question,
            "answer": response_body['response'],
            "chart_data": response_body['chart_data'],
            "visualization_type": response_body['visualization_type'],
            "endpoint": endpoint,
            "extracted_data": response_body['extracted_data'],
            "confidence": confidence,
            "processing_steps": {
                "intent_classification": "success",
                "graphql_query": "success",
                "response_generation": "success"
            }
        }
        
        print("✅ Complete response ready")
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps(final_response)
        }
        
    except Exception as e:
        print(f"\n❌ ERROR in orchestrator: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({
                "error": str(e),
                "message": "Error processing request",
                "question": body.get('question', '') if 'body' in locals() else ''
            })
        }




# For local testing
if __name__ == "__main__":
    # This won't work locally because it needs to invoke other Lambdas
    # But shows the structure
    test_event = {
        "body": json.dumps({
            "question": "What is the revenue from my total firm orders?"
        })
    }
    
    print("Orchestrator Lambda - requires AWS Lambda environment to run")
    print("Deploy to AWS and test with:")
    print("aws lambda invoke --function-name FactoryTwin-Orchestrator --payload file://test.json out.json")

