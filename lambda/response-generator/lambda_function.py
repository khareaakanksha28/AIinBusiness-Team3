"""
Lambda Function: Data Processor & Response Generator

Purpose: Processes GraphQL data and generates natural language responses using Groq LLM
"""

import json
import os
from typing import Dict, Any, List, Union

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


def extract_value_from_donut(data: Dict[str, Any], extraction_type: str) -> float:
    """
    Extract specific quantity from donut chart data (using quantity instead of value)
    """
    stack_data_list = data.get("stackDataList", [])
    
    if extraction_type == "firm_order":
        for item in stack_data_list:
            if item.get("name") == "Firm Order":
                return float(item.get("quantity", 0))
    
    elif extraction_type == "overdue":
        for item in stack_data_list:
            if item.get("name") == "Overdue":
                return float(item.get("quantity", 0))
    
    elif extraction_type == "forecasted":
        for item in stack_data_list:
            if item.get("name") == "Forecasted":
                return float(item.get("quantity", 0))
    
    elif extraction_type == "total":
        total = 0.0
        for item in stack_data_list:
            total += float(item.get("quantity", 0))
        return total
    
    return 0.0


def extract_value_from_histogram(data: List[Dict[str, Any]], extraction_type: str) -> Any:
    """
    Extract specific quantity from histogram data (using quantity instead of value)
    """
    if extraction_type == "monthly_count":
        # Count months with firm orders
        count = 0
        for period in data:
            stack_data_list = period.get("stackDataList", [])
            for item in stack_data_list:
                if item.get("name") == "Firm Order" and item.get("quantity", 0) > 0:
                    count += 1
                    break
        return count
    
    elif extraction_type == "average":
        # Calculate average monthly quantity
        total_quantity = 0.0
        period_count = 0
        
        for period in data:
            stack_data_list = period.get("stackDataList", [])
            period_total = sum(float(item.get("quantity", 0)) for item in stack_data_list)
            total_quantity += period_total
            period_count += 1
        
        return total_quantity / period_count if period_count > 0 else 0.0
    
    elif extraction_type == "highest_month":
        # Find month with highest total quantity
        max_quantity = 0.0
        max_period = None
        
        for period in data:
            stack_data_list = period.get("stackDataList", [])
            period_total = sum(float(item.get("quantity", 0)) for item in stack_data_list)
            if period_total > max_quantity:
                max_quantity = period_total
                max_period = period
        
        return {
            "startDate": max_period.get("startDate") if max_period else None,
            "quantity": max_quantity
        }
    
    return None


def format_quantity(value: float) -> str:
    """
    Format number as quantity with units
    """
    return f"{int(value):,} units"


def decide_visualization(
    question: str,
    current_endpoint: str,
    current_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    alternative_data: Union[Dict[str, Any], List[Dict[str, Any]], None],
    alternative_endpoint: str,
    all_available_data: Dict[str, Any],
    conversation_history: str = ""
) -> Dict[str, Any]:
    """
    AGENTIC: Use LLM to decide which visualization is best for the user's question
    Returns: {
        "endpoint": chosen endpoint,
        "data": chosen data,
        "visualization_type": "donut" or "stacked-bar",
        "reasoning": why this was chosen
    }
    """
    # Prepare context about available data
    has_donut = bool(all_available_data.get("donut"))
    has_histogram = bool(all_available_data.get("histogram"))
    
    data_context = f"""Available visualizations:
- Donut Chart: {'Available' if has_donut else 'Not available'} - Shows aggregate totals (Firm Order, Overdue, Forecasted)
- Histogram/Bar Chart: {'Available' if has_histogram else 'Not available'} - Shows time-based breakdown by month

Current visualization: {current_endpoint}
"""
    
    decision_prompt = f"""You are an AI agent that decides which visualization is best for answering user questions.

User Question: {question}
{data_context}
{conversation_history}

Based on the user's question, decide which visualization type would be most helpful:
- Use DONUT chart if the question is about: totals, aggregates, overall demand, percentages, comparisons between categories
- Use HISTOGRAM/BAR chart if the question is about: time trends, monthly breakdown, projections over time, specific months, patterns over time

Respond with ONLY a JSON object:
{{
    "visualization_type": "donut" or "stacked-bar",
    "endpoint": "demandByFulfillmentDonut" or "demandByFulfillmentHistogram",
    "reasoning": "brief explanation of why this visualization is best"
}}

Examples:
Question: "What is the total demand?" → {{"visualization_type": "donut", "endpoint": "demandByFulfillmentDonut", "reasoning": "Total demand is an aggregate question, best shown in donut chart"}}
Question: "Show me monthly trends" → {{"visualization_type": "stacked-bar", "endpoint": "demandByFulfillmentHistogram", "reasoning": "Monthly trends require time-based histogram"}}
"""
    
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a data visualization expert. Always respond with valid JSON only."},
                {"role": "user", "content": decision_prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )
        
        llm_response = response.choices[0].message.content.strip()
        # Extract JSON
        import re
        json_match = re.search(r'\{[^}]+\}', llm_response, re.DOTALL)
        if json_match:
            decision = json.loads(json_match.group())
            
            # Determine which data to use
            chosen_endpoint = decision.get("endpoint", current_endpoint)
            if chosen_endpoint == "demandByFulfillmentDonut" and has_donut:
                chosen_data = all_available_data.get("donut", current_data)
            elif chosen_endpoint == "demandByFulfillmentHistogram" and has_histogram:
                chosen_data = all_available_data.get("histogram", current_data)
            else:
                # Fallback to current data if chosen isn't available
                chosen_data = current_data
                chosen_endpoint = current_endpoint
                decision["visualization_type"] = "donut" if current_endpoint == "demandByFulfillmentDonut" else "stacked-bar"
            
            return {
                "endpoint": chosen_endpoint,
                "data": chosen_data,
                "visualization_type": decision.get("visualization_type", "donut"),
                "reasoning": decision.get("reasoning", "Selected based on question type")
            }
        else:
            # Fallback
            return {
                "endpoint": current_endpoint,
                "data": current_data,
                "visualization_type": "donut" if current_endpoint == "demandByFulfillmentDonut" else "stacked-bar",
                "reasoning": "Using current visualization (LLM decision parsing failed)"
            }
    except Exception as e:
        print(f"⚠️  Visualization decision failed: {e}, using current")
        # Fallback to current
        return {
            "endpoint": current_endpoint,
            "data": current_data,
            "visualization_type": "donut" if current_endpoint == "demandByFulfillmentDonut" else "stacked-bar",
            "reasoning": f"Using current visualization (error: {str(e)[:50]})"
        }


def generate_response(
    question: str,
    endpoint: str,
    extraction_type: str,
    graphql_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    extracted_value: Any,
    conversation_history: str = "",
    is_followup: bool = False,
    visualization_decision: Dict[str, Any] = None,
    date_range: Dict[str, Any] = None
) -> str:
    """
    Use Groq LLM to generate natural language response
    """
    
    # Format the extracted quantity
    if isinstance(extracted_value, (int, float)):
        formatted_value = format_quantity(extracted_value) if endpoint == "demandByFulfillmentDonut" else str(int(extracted_value))
    elif isinstance(extracted_value, dict):
        formatted_value = format_quantity(extracted_value.get("quantity", 0.0))
    else:
        formatted_value = str(extracted_value)
    
    # Prepare detailed context about the data
    if endpoint == "demandByFulfillmentDonut":
        stack_data = graphql_data.get("stackDataList", [])
        
        # Extract detailed breakdown
        firm_order = next((item for item in stack_data if item.get("name") == "Firm Order"), {})
        overdue = next((item for item in stack_data if item.get("name") == "Overdue"), {})
        forecasted = next((item for item in stack_data if item.get("name") == "Forecasted"), {})
        
        firm_order_qty = firm_order.get("quantity", 0)
        overdue_qty = overdue.get("quantity", 0)
        forecasted_qty = forecasted.get("quantity", 0)
        
        total_qty = firm_order_qty + overdue_qty + forecasted_qty
        
        # Build detailed context - only include non-zero quantities
        context_parts = []
        if firm_order_qty > 0:
            context_parts.append(f"Firm Orders: {format_quantity(firm_order_qty)}")
        if overdue_qty > 0:
            context_parts.append(f"Overdue: {format_quantity(overdue_qty)}")
        if forecasted_qty > 0:
            context_parts.append(f"Forecasted: {format_quantity(forecasted_qty)}")
        
        context = f"Complete data breakdown:\n" + "\n".join(context_parts) + f"\nTotal: {format_quantity(total_qty)}"
        
        # Calculate and include percentages for better context
        if total_qty > 0:
            context += "\n\nPercentage Breakdown:"
            if firm_order_qty > 0:
                firm_pct = (firm_order_qty / total_qty * 100)
                context += f"\n- Firm Orders: {firm_pct:.1f}% of total"
            if overdue_qty > 0:
                overdue_pct = (overdue_qty / total_qty * 100)
                context += f"\n- Overdue: {overdue_pct:.1f}% of total"
            if forecasted_qty > 0:
                forecasted_pct = (forecasted_qty / total_qty * 100)
                context += f"\n- Forecasted: {forecasted_pct:.1f}% of total"
            
            # Add ratios
            if firm_order_qty > 0 and forecasted_qty > 0:
                ratio = forecasted_qty / firm_order_qty
                context += f"\n- Forecasted is {ratio:.2f}x Firm Order quantity"
        
        # Important: Only mention categories that have non-zero values. Do not mention zero values in your response.
        
        # Add analysis hints for projected demand questions
        analysis_hints = ""
        if "projected" in question.lower() or "forecast" in question.lower() or "next" in question.lower() or "future" in question.lower():
            if forecasted_qty > 0:
                forecasted_pct = (forecasted_qty / total_qty * 100) if total_qty > 0 else 0
                analysis_hints = f"\n\nFor projected/forecasted demand analysis:\n"
                analysis_hints += f"- Forecasted demand represents {forecasted_pct:.1f}% of total demand\n"
                analysis_hints += f"- Forecasted quantity: {format_quantity(forecasted_qty)}\n"
                if firm_order_qty > 0:
                    ratio = forecasted_qty / firm_order_qty
                    analysis_hints += f"- Forecasted is {ratio:.1f}x the Firm Order quantity\n"
                analysis_hints += f"- This represents expected future demand based on current patterns"
            
        if "overdue" in question.lower() or "late" in question.lower():
            if overdue_qty > 0:
                overdue_pct = (overdue_qty / total_qty * 100) if total_qty > 0 else 0
                analysis_hints = f"\n\nFor overdue analysis:\n"
                analysis_hints += f"- Overdue orders represent {overdue_pct:.1f}% of total demand\n"
                analysis_hints += f"- Overdue quantity: {format_quantity(overdue_qty)}\n"
                analysis_hints += f"- This indicates orders that are past their due date and need attention"
        
        context += analysis_hints
        
    elif endpoint == "demandByFulfillmentHistogram":
        # For histogram, provide detailed period-by-period breakdown
        periods = graphql_data if isinstance(graphql_data, list) else [graphql_data]
        context_parts = [f"Data contains {len(periods)} time periods with the following breakdown:\n"]
        
        for i, period in enumerate(periods):
            if period and period.get("stackDataList"):
                start_date = period.get("startDate", "Unknown")
                # Format date
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    date_str = date_obj.strftime("%B %Y")
                except:
                    date_str = start_date
                
                period_data = []
                total_period_qty = 0
                for item in period["stackDataList"]:
                    if item and item.get("name"):
                        qty = item.get("quantity", 0)
                        if qty > 0:
                            period_data.append(f"  - {item['name']}: {format_quantity(qty)}")
                            total_period_qty += qty
                
                if period_data:
                    context_parts.append(f"\n{date_str}:")
                    context_parts.extend(period_data)
                    context_parts.append(f"  Total: {format_quantity(total_period_qty)}")
        
        # Calculate overall statistics
        all_quantities = []
        category_totals = {}
        for period in periods:
            if period and period.get("stackDataList"):
                for item in period["stackDataList"]:
                    if item and item.get("name") and item.get("quantity", 0) > 0:
                        name = item["name"]
                        qty = item.get("quantity", 0)
                        category_totals[name] = category_totals.get(name, 0) + qty
                        all_quantities.append(qty)
        
        if category_totals:
            context_parts.append(f"\n\nOverall Summary:")
            for name, total_qty in category_totals.items():
                context_parts.append(f"  - {name}: {format_quantity(total_qty)}")
            if all_quantities:
                avg_qty = sum(all_quantities) / len(all_quantities)
                max_qty = max(all_quantities)
                min_qty = min(all_quantities)
                context_parts.append(f"\n  Average per period: {format_quantity(avg_qty)}")
                context_parts.append(f"  Peak period: {format_quantity(max_qty)}")
                context_parts.append(f"  Lowest period: {format_quantity(min_qty)}")
        
        context = "\n".join(context_parts)
    else:
        context = f"Data contains {len(graphql_data)} time periods"
    
    # Determine chart type for context
    chart_type = "donut chart" if endpoint == "demandByFulfillmentDonut" else "histogram/bar chart"
    
    # Add date range context if specified
    date_range_context = ""
    if date_range and (date_range.get('from') or date_range.get('until')):
        from_date = date_range.get('from', '')
        until_date = date_range.get('until', '')
        if from_date and until_date:
            # Format dates for readability
            try:
                from datetime import datetime
                from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                until_dt = datetime.fromisoformat(until_date.replace('Z', '+00:00'))
                from_str = from_dt.strftime("%B %Y")
                until_str = until_dt.strftime("%B %Y")
                date_range_context = f"\n\n📅 Date Range: The data shown covers the period from {from_str} to {until_str}. Make sure to mention this specific time period in your response."
            except:
                date_range_context = f"\n\n📅 Date Range: The data shown covers the period from {from_date} to {until_date}. Make sure to mention this specific time period in your response."
    
    # Build follow-up context if applicable
    followup_context = ""
    if is_followup and conversation_history:
        followup_context = f"\n\n{conversation_history}\n\nThis is a follow-up question. Use the previous conversation context to provide a more detailed answer about the data that was already shown."
    
    # Add agentic decision context
    agentic_context = ""
    if visualization_decision and visualization_decision.get("reasoning"):
        agentic_context = f"\n\n🤖 Visualization Decision: I chose to show a {visualization_decision.get('visualization_type', 'chart')} because {visualization_decision.get('reasoning', 'it best answers your question')}. Make sure to explain why this visualization is helpful for answering the question."
    
    system_prompt = f"""You are an AI assistant for FactoryTwin manufacturing software.
Your job is to analyze manufacturing data and answer user questions in a clear, natural, and insightful way.

User Question: {question}
Extracted Value: {formatted_value}
Data Context:
{context}
{date_range_context}
{followup_context}
{agentic_context}

The user will see a {chart_type} visualization showing this data. Your response should explain the chart in detail.

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:
1. **EXPLAIN THE CHART IN DETAIL**: Start by describing what the chart visualization shows. For donut charts, describe each segment's size, color, and position. For histograms, describe the bars, trends, and time periods.

2. **PROVIDE COMPREHENSIVE ANALYSIS**: Don't just state numbers - analyze them deeply:
   - Break down each category with specific quantities
   - Calculate and explain percentages (e.g., "Firm Orders represent 25% of total demand")
   - Compare categories (e.g., "Forecasted is 3x larger than Firm Orders")
   - Explain what these numbers mean in business terms

3. **For donut charts**: 
   - Describe each segment: Firm Order (medium blue), Overdue (dark blue), Forecasted (gray)
   - Explain the size of each segment relative to the whole
   - Calculate percentages for each category
   - Explain what each category represents and why it matters

4. **For histogram/bar charts**:
   - Describe the time periods shown
   - Identify trends: increasing, decreasing, or stable
   - Point out peaks and valleys with specific months
   - Explain patterns across the timeline
   - Calculate averages and totals

5. **PROVIDE BUSINESS INSIGHTS**: Go beyond numbers:
   - What does this data mean for production planning?
   - What decisions should be made based on this data?
   - What are the implications for inventory management?
   - What risks or opportunities does this reveal?

6. **Be detailed but concise**: Your response should be between 300-500 words. Be comprehensive but stay within the 500 word limit. Provide thorough explanations without being overly verbose.

7. **Include specific numbers**: Always mention exact quantities, percentages, and ratios. Use the data provided.

8. **Be conversational but professional**: Write as if explaining to a colleague who needs to understand the data.

9. **If this is a follow-up question**: Reference the previous conversation and provide additional details or different perspectives on the same data.

10. **IMPORTANT**: Only mention categories that have non-zero values. Do NOT mention categories with zero values.

Your response MUST be detailed, comprehensive, and insightful. Aim for 300-500 words (MAXIMUM 500 words) with specific numbers, percentages, and business insights.

REMEMBER:
- Start with a clear description of what the chart shows
- Break down EVERY number with context
- Calculate and explain ALL percentages
- Provide multiple business insights
- Be conversational and engaging
- Use specific examples from the data
- Keep response between 300-500 words - be concise but thorough
- DO NOT exceed 500 words

Be thorough but concise. Stay within the 500 word limit.
"""

    try:
        client = get_groq_client()
        
        # Build user message
        user_message = question
        if is_followup:
            user_message = f"{question}\n\nIMPORTANT: This is a follow-up question. Provide a detailed, comprehensive answer using the data context provided above. Be thorough and explain everything in detail."
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,  # Increased for more natural, detailed responses
            max_tokens=700  # Set for ~500 words (approximately 1.4 tokens per word)
        )
        
        llm_response = response.choices[0].message.content.strip()
        return llm_response
        
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to simple template-based response
        print("⚠️  Falling back to template response due to error")
        if endpoint == "demandByFulfillmentDonut":
            if extraction_type == "firm_order":
                return f"Your total firm order revenue is {formatted_value}."
            elif extraction_type == "total":
                stack_data = graphql_data.get("stackDataList", [])
                breakdown_items = []
                for item in stack_data:
                    name = item.get("name", "")
                    qty = format_quantity(item.get("quantity", 0.0))
                    breakdown_items.append(f"{name}: {qty}")
                breakdown = ", ".join(breakdown_items)
                return f"Your total demand across all order types is {formatted_value}, which includes {breakdown}."
            elif extraction_type == "overdue":
                return f"You have {formatted_value} in overdue orders."
            else:
                return f"The {extraction_type} value is {formatted_value}."
        else:
            if extraction_type == "monthly_count":
                return f"You have firm orders in {extracted_value} months."
            elif extraction_type == "average":
                return f"Your average monthly revenue is {formatted_value}."
            else:
                return f"The extracted value is {formatted_value}."


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
        
        question = body.get("question", "")
        endpoint = body.get("endpoint", "")
        extraction_type = body.get("extraction_type", "")
        graphql_data = body.get("graphql_data", {})
        conversation_history = body.get("conversation_history", "")
        is_followup = body.get("is_followup", False)
        date_range = body.get("date_range")  # Extract date range from request
        # Agentic: Alternative data for LLM to choose visualization
        alternative_data = body.get("alternative_data")
        alternative_endpoint = body.get("alternative_endpoint")
        all_available_data = body.get("all_available_data", {})
        
        if not question or not endpoint or not extraction_type or not graphql_data:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing required fields",
                    "message": "Please provide 'question', 'endpoint', 'extraction_type', and 'graphql_data'"
                })
            }
        
        # Extract value based on endpoint and extraction type
        if endpoint == "demandByFulfillmentDonut":
            extracted_value = extract_value_from_donut(graphql_data, extraction_type)
        elif endpoint == "demandByFulfillmentHistogram":
            extracted_value = extract_value_from_histogram(graphql_data, extraction_type)
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Unknown endpoint",
                    "message": f"Endpoint '{endpoint}' is not supported"
                })
            }
        
        # AGENTIC: Let LLM decide visualization type and data to use
        print("🤖 Agentic Decision: LLM choosing visualization...")
        visualization_decision = decide_visualization(
            question,
            endpoint,
            graphql_data,
            alternative_data,
            alternative_endpoint,
            all_available_data,
            conversation_history
        )
        
        # Use LLM's decision
        selected_data = visualization_decision["data"]
        selected_endpoint = visualization_decision["endpoint"]
        visualization_type = visualization_decision["visualization_type"]
        
        # Re-extract value if data changed
        if selected_endpoint != endpoint:
            if selected_endpoint == "demandByFulfillmentDonut":
                extracted_value = extract_value_from_donut(selected_data, extraction_type)
            elif selected_endpoint == "demandByFulfillmentHistogram":
                extracted_value = extract_value_from_histogram(selected_data, extraction_type)
        
        # Generate natural language response with agentic context
        response_text = generate_response(
            question,
            selected_endpoint,
            extraction_type,
            selected_data,
            extracted_value,
            conversation_history=conversation_history,
            is_followup=is_followup,
            visualization_decision=visualization_decision,
            date_range=date_range
        )
        
        # Format extracted quantity for response
        if isinstance(extracted_value, (int, float)):
            formatted_value = format_quantity(extracted_value) if selected_endpoint == "demandByFulfillmentDonut" else str(int(extracted_value))
        elif isinstance(extracted_value, dict):
            formatted_value = format_quantity(extracted_value.get("quantity", 0.0))
        else:
            formatted_value = str(extracted_value)
        
        print(f"Generated response: {response_text[:100]}...")
        print(f"🤖 LLM chose visualization: {visualization_type} ({selected_endpoint})")
        
        # Use LLM's visualization decision
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "question": question,
                "response": response_text,
                "endpoint": endpoint,
                "extraction_type": extraction_type,
                "visualization_type": visualization_type,
                "chart_data": selected_data,  # Use LLM-selected data
                "agentic_decision": visualization_decision.get("reasoning", ""),  # Why LLM chose this
                "extracted_data": {
                "quantity": extracted_value,
                    "formatted_value": formatted_value
                }
            })
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "message": "Internal server error during response generation"
            })
        }

