# Response Generation Flow

## Complete Flow: User Query → Response

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER ASKS QUESTION                            │
│              "What is the total demand?"                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: FRONTEND (app.js)                                      │
│  - User types question in chat input                            │
│  - sendQuestion() sends POST to /query                          │
│  - Shows loading indicator                                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: BACKEND API (local_server.py)                          │
│  - Flask route /query receives POST request                     │
│  - Calls process_question(user_question)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: INTENT CLASSIFICATION                                  │
│  (lambda/intent-classifier/lambda_function.py)                 │
│                                                                  │
│  Uses Groq LLM (llama-3.3-70b-versatile) to:                  │
│  1. Analyze user question                                       │
│  2. Determine which GraphQL endpoint to use:                    │
│     - demandByFulfillmentDonut (for totals/aggregates)          │
│     - demandByFulfillmentHistogram (for time-based data)        │
│  3. Determine extraction_type:                                   │
│     - "total", "firm_order", "overdue", "forecasted"            │
│     - "monthly_count", "average", "highest_month"              │
│  4. Return confidence score (0.0-1.0)                           │
│                                                                  │
│  Example Output:                                                │
│  {                                                              │
│    "endpoint": "demandByFulfillmentDonut",                      │
│    "extraction_type": "total",                                  │
│    "confidence": 0.95                                           │
│  }                                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: GET ALL SIMULATIONS                                    │
│  (lambda/graphql-client/lambda_function.py)                    │
│                                                                  │
│  - Queries GraphQL API: listSimulations                        │
│  - Retrieves all available simulation IDs                       │
│  - Example: Returns 8 simulation identifiers                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: QUERY GRAPHQL FOR ALL SIMULATIONS                      │
│  (lambda/graphql-client/lambda_function.py)                    │
│                                                                  │
│  For each simulation ID:                                        │
│  1. Build GraphQL query based on endpoint                       │
│  2. Set variables (simulationId, date ranges, etc.)             │
│  3. Send POST to GraphQL API (http://10.1.10.184:9000/graphql)   │
│  4. Parse response and extract data                             │
│                                                                  │
│  Example Query (Donut):                                         │
│  query {                                                        │
│    simulation(identifier: "uuid") {                             │
│      charts {                                                    │
│        demandByFulfillmentDonut {                               │
│          stackDataList {                                        │
│            name                                                  │
│            quantity                                              │
│            value                                                 │
│          }                                                       │
│        }                                                         │
│      }                                                           │
│    }                                                             │
│  }                                                               │
│                                                                  │
│  Returns data from all simulations                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: AGGREGATE DATA FROM ALL SIMULATIONS                    │
│  (local_server.py - aggregate_simulation_data())               │
│                                                                  │
│  For Donut Charts:                                              │
│  - Combines stackDataList from all simulations                 │
│  - Sums quantities and values by category:                      │
│    * Firm Order: sum of all firm orders                        │
│    * Overdue: sum of all overdue                                │
│    * Forecasted: sum of all forecasted                          │
│                                                                  │
│  For Histogram Charts:                                          │
│  - Returns first simulation's data (or aggregates by period)    │
│                                                                  │
│  Special Feature: LLM-Based Forecasting                         │
│  - If Forecasted is missing/zero but Firm Order exists:           │
│    1. Calls predict_forecasted_demand()                         │
│    2. Uses Groq LLM to predict forecasted demand                │
│    3. LLM analyzes Firm Order patterns                          │
│    4. Returns predicted Forecasted quantity/value               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: EXTRACT VALUE                                          │
│  (lambda/response-generator/lambda_function.py)                 │
│                                                                  │
│  Based on extraction_type:                                      │
│  - extract_value_from_donut():                                  │
│    * "total": sums all quantities                               │
│    * "firm_order": gets Firm Order quantity                    │
│    * "overdue": gets Overdue quantity                           │
│    * "forecasted": gets Forecasted quantity                     │
│                                                                  │
│  - extract_value_from_histogram():                              │
│    * "monthly_count": counts months with data                  │
│    * "average": calculates average per period                    │
│    * "highest_month": finds peak period                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: BUILD DETAILED CONTEXT                                 │
│  (lambda/response-generator/lambda_function.py)                 │
│                                                                  │
│  For Donut Charts:                                              │
│  - Extracts Firm Order, Overdue, Forecasted quantities         │
│  - Calculates percentages and ratios                             │
│  - Builds context string with breakdown                         │
│  - Adds analysis hints for specific question types               │
│                                                                  │
│  For Histogram Charts:                                          │
│  - Period-by-period breakdown with dates                        │
│  - Quantities per period                                        │
│  - Overall statistics: totals, averages, peaks, lows             │
│  - Category summaries across all periods                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: GENERATE NATURAL LANGUAGE RESPONSE                     │
│  (lambda/response-generator/lambda_function.py)                 │
│                                                                  │
│  Uses Groq LLM (llama-3.3-70b-versatile) with:                  │
│                                                                  │
│  System Prompt includes:                                         │
│  - User's question                                               │
│  - Extracted value (formatted)                                   │
│  - Detailed data context (breakdown, statistics)                │
│  - Chart type (donut or histogram)                              │
│  - Instructions to explain charts in detail                      │
│                                                                  │
│  Instructions to LLM:                                            │
│  1. EXPLAIN THE CHART: Describe visualization                   │
│  2. ANALYZE THE DATA: Break down numbers, percentages            │
│  3. For donut: Explain each segment, sizes, percentages         │
│  4. For histogram: Explain trends, peaks, patterns                │
│  5. PROVIDE INSIGHTS: Business implications                       │
│  6. Be conversational and engaging                              │
│                                                                  │
│  LLM Parameters:                                                 │
│  - Model: llama-3.3-70b-versatile                                │
│  - Temperature: 0.3 (consistent responses)                      │
│  - Max Tokens: 1000 (detailed explanations)                     │
│                                                                  │
│  Returns: Natural language response explaining the chart        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 10: FORMAT RESPONSE                                       │
│  (lambda/response-generator/lambda_function.py - lambda_handler)│
│                                                                  │
│  Returns JSON response:                                          │
│  {                                                              │
│    "response": "The total demand currently stands at...",       │
│    "chart_data": { ... },                                       │
│    "visualization_type": "donut",                               │
│    "extracted_data": {                                          │
│      "quantity": 55910,                                         │
│      "formatted_value": "55,910 units"                         │
│    }                                                             │
│  }                                                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 11: BACKEND RETURNS COMPLETE RESPONSE                     │
│  (local_server.py)                                              │
│                                                                  │
│  Combines all data:                                              │
│  {                                                              │
│    "question": "What is the total demand?",                    │
│    "answer": "The total demand currently stands at...",        │
│    "chart_data": { ... },                                       │
│    "visualization_type": "donut",                               │
│    "endpoint": "demandByFulfillmentDonut",                      │
│    "extracted_data": { ... },                                   │
│    "confidence": 0.95                                          │
│  }                                                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 12: FRONTEND DISPLAYS RESPONSE                            │
│  (frontend/app.js)                                              │
│                                                                  │
│  1. Receives JSON response                                      │
│  2. Displays answer text in chat bubble                         │
│  3. Calls showVisualization() with chart_data                   │
│  4. Renders chart using Chart.js:                               │
│     - Donut chart: Shows segments with quantities               │
│     - Histogram: Shows stacked bars by time period               │
│  5. Adds tooltips with detailed information                    │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Intent Classification
- **File**: `lambda/intent-classifier/lambda_function.py`
- **Purpose**: Determines which data endpoint to query
- **Method**: Uses Groq LLM to analyze question intent
- **Output**: `{endpoint, extraction_type, confidence}`

### 2. GraphQL Client
- **File**: `lambda/graphql-client/lambda_function.py`
- **Purpose**: Fetches data from FactoryTwin GraphQL API
- **Method**: Builds and executes GraphQL queries
- **Output**: Raw data from API

### 3. Data Aggregation
- **File**: `local_server.py` - `aggregate_simulation_data()`
- **Purpose**: Combines data from multiple simulations
- **Method**: Sums quantities/values by category
- **Special**: LLM-based forecasting if Forecasted is missing

### 4. Response Generator
- **File**: `lambda/response-generator/lambda_function.py`
- **Purpose**: Generates natural language explanation
- **Method**: 
  1. Extracts specific value based on extraction_type
  2. Builds detailed context about the data
  3. Uses Groq LLM to generate comprehensive response
  4. Returns formatted response with chart data

## Data Flow Example

**User Question**: "What is the total demand?"

1. **Intent Classification** → `{endpoint: "demandByFulfillmentDonut", extraction_type: "total"}`
2. **GraphQL Query** → Fetches data from 8 simulations
3. **Aggregation** → Combines all simulations:
   ```
   Firm Order: 13,952 units
   Overdue: 0 units
   Forecasted: 41,958 units
   Total: 55,910 units
   ```
4. **Extract Value** → `55910` (total quantity)
5. **Build Context** → Detailed breakdown with percentages
6. **LLM Response** → "The total demand currently stands at 55,910 units. This total is comprised of two key components: firm orders and forecasted demand..."
7. **Frontend** → Displays text + renders donut chart

## LLM Usage

The system uses **Groq LLM** in two places:

1. **Intent Classification** (Step 3)
   - Model: `llama-3.3-70b-versatile`
   - Temperature: 0.2 (very consistent)
   - Max Tokens: 200
   - Purpose: Classify question intent

2. **Response Generation** (Step 9)
   - Model: `llama-3.3-70b-versatile`
   - Temperature: 0.3 (consistent but slightly creative)
   - Max Tokens: 1000 (detailed explanations)
   - Purpose: Generate natural language response with chart explanations

3. **Forecasted Demand Prediction** (Step 6, optional)
   - Model: `llama-3.3-70b-versatile`
   - Temperature: 0.3
   - Max Tokens: 200
   - Purpose: Predict forecasted demand if missing

## Error Handling

- If intent classification fails → Falls back to keyword matching
- If GraphQL query fails → Tries next simulation, logs warning
- If no data retrieved → Returns helpful error message
- If LLM fails → Falls back to template-based response
- If response generation fails → Returns error with details

## Performance

- **Intent Classification**: ~1-2 seconds
- **GraphQL Queries**: ~2-3 seconds (for all simulations)
- **Data Aggregation**: <1 second
- **Response Generation**: ~2-4 seconds
- **Total**: ~5-10 seconds per question

