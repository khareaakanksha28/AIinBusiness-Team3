# FactoryTwin AI - Intelligent Manufacturing Data Assistant

An AI-powered chatbot that analyzes manufacturing data from FactoryTwin GraphQL API using Groq LLM for natural language queries and intelligent data visualization.

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English about your manufacturing data
- **Dynamic Date Ranges**: Extract and query specific date ranges from natural language (e.g., "Dec 25 to May 26")
- **Intelligent Intent Classification**: Automatically determines which data endpoint to query
- **LLM-Powered Summaries**: Generates comprehensive 300-500 word analyses with business insights
- **Dynamic Visualizations**: Charts adjust based on your query (donut charts, histograms)
- **Multi-Simulation Support**: Queries and aggregates data from multiple simulations
- **Conversational AI**: Handles acknowledgments and follow-up questions naturally

## 📁 Project Structure

```
factorytwin-ai/
├── lambda/                    # AWS Lambda functions
│   ├── intent-classifier/    # Classifies user intent and extracts date ranges
│   ├── graphql-client/       # Queries FactoryTwin GraphQL API
│   ├── response-generator/   # Generates LLM responses with Groq
│   └── orchestrator/          # Orchestrates the complete flow
├── frontend/                  # Chat interface
│   ├── app.js                # Main frontend logic
│   ├── index.html            # Chat interface
│   └── styles.css            # Styling
└── config/                    # Configuration files
    └── knowledge-graph.json   # Endpoint metadata and mappings
```

## 🛠️ Setup

### Prerequisites

- Python 3.9+
- Groq API Key (free at https://console.groq.com/)
- Access to FactoryTwin GraphQL API (via VPN or network access)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd factorytwin-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Lambda dependencies**
   ```bash
   cd lambda/intent-classifier && pip install -r requirements.txt
   cd ../graphql-client && pip install -r requirements.txt
   cd ../response-generator && pip install -r requirements.txt
   cd ../..
   ```

4. **Configure environment variables**
   
   Create a `local_config.sh` file (use `config.example.sh` as a template):
   ```bash
   export GROQ_API_KEY="your-groq-api-key"
   export GRAPHQL_URL="http://your-graphql-server:9000/graphql"
   export SIMULATION_ID="your-simulation-id"
   ```

## 🔧 Lambda Functions

### Intent Classifier (`lambda/intent-classifier/`)
- **Purpose**: Classifies user questions and extracts date ranges from natural language
- **Model**: Groq Llama 3.3 70B
- **Output**: `{endpoint, extraction_type, date_range, confidence}`
- **Features**: 
  - Detects conversational acknowledgments ("thank you", etc.)
  - Extracts date ranges from queries like "Dec 25 to May 26"
  - Maps questions to appropriate GraphQL endpoints

### GraphQL Client (`lambda/graphql-client/`)
- **Purpose**: Queries FactoryTwin GraphQL API
- **Features**: 
  - Dynamic date range support
  - Multi-simulation queries
  - Automatic period boundary generation for histograms
- **Endpoints**: 
  - `demandByFulfillmentDonut` - Total aggregate demand
  - `demandByFulfillmentHistogram` - Monthly breakdown

### Response Generator (`lambda/response-generator/`)
- **Purpose**: Generates natural language responses using Groq LLM
- **Model**: Groq Llama 3.3 70B
- **Output**: 300-500 word comprehensive analyses
- **Features**:
  - Business insights and recommendations
  - Context-aware explanations
  - Visualization recommendations

## 📊 Supported Queries

- **Total Demand**: "What is my total demand?"
- **Firm Orders**: "Show me my firm orders"
- **Forecasted Demand**: "What is my forecasted demand?"
- **Date Range Queries**: "What is projected demand from Dec 25 to May 26?"
- **Monthly Analysis**: "Show me demand from January 2025 to June 2025"
- **Averages**: "What is my average monthly revenue?"
- **Highest Month**: "Which month has the highest demand?"
- **Conversational**: "Thank you" → Simple acknowledgment (no data query)

## 🏗️ Architecture

The system follows a microservices architecture with Lambda functions:

1. **User Query** → Frontend (`frontend/app.js`)
2. **Intent Classification** → `intent-classifier` Lambda
3. **Data Fetching** → `graphql-client` Lambda
4. **Response Generation** → `response-generator` Lambda
5. **Visualization** → Frontend renders charts (donut/histogram)

## 🔐 Security Notes

- **Never commit API keys** to the repository
- Use environment variables for sensitive configuration
- `local_config.sh` and `local_server.py` are excluded from git (see `.gitignore`)
- Always use `config.example.sh` as a template for configuration

## 📝 Documentation

- `RESPONSE_GENERATION_FLOW.md` - Complete system flow and data processing
- `INTERACTIVE_FLOW.md` - Frontend interaction flow
- `DEMO_GUIDE.md` - Demo and testing guide
- `LLM_FORECASTING.md` - LLM forecasting capabilities
- `SCHEMA_UPDATES.md` - GraphQL schema documentation

## 🧪 Testing

Each Lambda function includes test files:
- `lambda/*/test_local.py` - Local testing scripts

**Note**: Test files are excluded from git as they may contain local configuration.

## 🚀 Deployment

### AWS Lambda Deployment

1. Package each Lambda function:
   ```bash
   cd lambda/intent-classifier
   zip -r function.zip lambda_function.py requirements.txt
   ```

2. Deploy to AWS Lambda via AWS Console or CLI

3. Configure environment variables in Lambda:
   - `GROQ_API_KEY`
   - `GRAPHQL_URL`
   - `SIMULATION_ID`

### Frontend Deployment

The frontend can be deployed to any static hosting service:
- AWS S3 + CloudFront
- Netlify
- Vercel
- GitHub Pages

Update the API endpoint in `frontend/app.js` to point to your deployed backend.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- **Groq** for fast and free LLM API
- **FactoryTwin** for GraphQL API and manufacturing data
- **Recharts** for data visualization

## 📧 Contact

[Your Contact Information]

