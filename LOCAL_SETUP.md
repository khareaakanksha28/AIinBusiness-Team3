# Local Mac Setup - FactoryTwin AI

Run everything locally on your Mac - **completely free!** No AWS needed.

## ✅ Benefits

- **Free**: No AWS costs
- **Fast**: Direct VPN connection from your Mac
- **Simple**: Everything runs locally
- **Easy Debugging**: See all logs in terminal

## Prerequisites

1. **Python 3.9+** (check with `python3 --version`)
2. **VPN Connected** (to access `10.1.10.184:9000`)
3. **Groq API Key** (free at https://console.groq.com/)

## Quick Start

### Step 1: Get Groq API Key (Free)

1. Go to https://console.groq.com/
2. Sign up (free)
3. Create API key
4. Copy the key

### Step 2: Configure

Edit `local_config.sh` and add your Groq API key:

```bash
export GROQ_API_KEY="your-actual-api-key-here"
```

### Step 3: Run

```bash
# Make sure VPN is connected first!
./run_local.sh
```

The server will start on `http://localhost:5000`

## Testing

### Test with curl:

```bash
# Health check
curl http://localhost:5000/health

# Ask a question
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the revenue from my total firm orders?"}'
```

### Test with Python:

```python
import requests

response = requests.post(
    'http://localhost:5000/query',
    json={'question': 'What is the revenue from my total firm orders?'}
)
print(response.json())
```

## API Endpoints

- **POST /query** - Main endpoint for questions
- **GET /health** - Health check
- **GET /** - API information

## Configuration

Edit `local_config.sh` to change:
- `GRAPHQL_URL` - Your GraphQL API URL
- `SIMULATION_ID` - Your simulation ID
- `GROQ_API_KEY` - Your Groq API key
- `AUTH_TOKEN` - Optional authentication token

## Troubleshooting

### "Cannot reach GraphQL API"
- Make sure VPN is connected
- Check `10.1.10.184:9000` is accessible
- Test with: `curl http://10.1.10.184:9000/graphql`

### "Module not found"
- Run: `pip install -r requirements-local.txt`
- Make sure virtual environment is activated

### "Groq API error"
- Check your API key is set: `echo $GROQ_API_KEY`
- Verify key is valid at https://console.groq.com/

## Architecture

```
User Question
    ↓
Local Server (Flask)
    ↓
Intent Classifier (Groq LLM)
    ↓
GraphQL Client (via VPN)
    ↓
Response Generator (Groq LLM)
    ↓
Natural Language Answer
```

## Next Steps

1. **Frontend Integration**: Update frontend to use `http://localhost:5000/query`
2. **Development**: All code is local, easy to modify and test
3. **Deployment**: When ready, deploy back to AWS or keep local

## Cost Comparison

| Solution | Cost |
|----------|------|
| AWS Lambda + VPC | ~$36-50/month |
| AWS Lambda + NAT Instance | ~$7-15/month |
| **Local Mac (this)** | **$0** ✅ |

Enjoy your free prototype! 🎉

