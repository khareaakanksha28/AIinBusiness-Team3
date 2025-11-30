#!/bin/bash
# Configuration Template for FactoryTwin AI
# Copy this to local_config.sh and fill in your values
# DO NOT commit local_config.sh to git (it's in .gitignore)

# GraphQL Configuration
export GRAPHQL_URL="http://your-graphql-server:9000/graphql"
export SIMULATION_ID="your-simulation-id-here"

# Groq API Key (for LLM)
# Get your free API key from: https://console.groq.com/
export GROQ_API_KEY="your-groq-api-key-here"
export GROQ_MODEL="llama-3.3-70b-versatile"

# Optional: Authentication token for GraphQL
# export AUTH_TOKEN="your-token-here"

echo "✅ Configuration template loaded"
echo "   Copy this file to local_config.sh and update with your values"
echo "   DO NOT commit local_config.sh to git!"

