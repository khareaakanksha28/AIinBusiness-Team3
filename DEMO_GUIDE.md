# FactoryTwin AI - Complete Demo Guide

## 🎉 Everything is Ready!

Your complete FactoryTwin AI system is now running locally on your Mac!

## What's Running

1. **Backend Server** (Port 5001)
   - API endpoint: `http://localhost:5001/query`
   - Health check: `http://localhost:5001/health`
   - Status: ✅ Running

2. **Frontend Server** (Port 8080)
   - Web interface: `http://localhost:8080`
   - Status: ✅ Running

## 🚀 Start the Demo

### Step 1: Open the Frontend

Open your browser and go to:
```
http://localhost:8080
```

Or run:
```bash
open http://localhost:8080
```

### Step 2: Try Example Questions

Click on any of the example questions:
- "What is the revenue from my total firm orders?"
- "How many months do I have firm demand?"
- "What is my total demand?"

Or type your own question!

### Step 3: See the Results

- **Chat Response**: Natural language answer
- **Visualization**: Interactive chart (donut or bar chart)
- **Confidence**: Shows how confident the AI is

## 📊 Chart Types

### Donut Chart
- Appears for: Total demand questions
- Shows: Breakdown by order type (Firm Orders, Overdue, Forecasted)
- Interactive: Hover to see values

### Stacked Bar Chart
- Appears for: Monthly/historical questions
- Shows: Time series data with stacked categories
- Interactive: Click legend to toggle categories

## 🎨 Features

- ✅ Modern, responsive UI
- ✅ Real-time chat interface
- ✅ Dynamic chart visualizations
- ✅ Confidence indicators
- ✅ Loading animations
- ✅ Error handling

## 🔧 Troubleshooting

### Frontend not loading?
```bash
# Check if frontend server is running
curl http://localhost:8080

# Restart if needed
cd ~/factorytwin-ai/frontend
python3 -m http.server 8080
```

### Backend not responding?
```bash
# Check if backend is running
curl http://localhost:5001/health

# Restart if needed
cd ~/factorytwin-ai
./run_local.sh
```

### Charts not showing?
- Check browser console (F12)
- Verify server is returning chart_data
- Make sure Chart.js loaded (check Network tab)

### CORS errors?
- Backend has CORS enabled
- Check server logs if issues persist

## 📝 Test Questions

Try these questions to see different visualizations:

1. **Donut Chart**:
   - "What is the revenue from my total firm orders?"
   - "What is my total demand?"
   - "Show me firm order revenue"

2. **Bar Chart** (if histogram data available):
   - "How many months do I have firm demand?"
   - "Show me monthly demand"

## 🎯 Complete Flow

```
User Question
    ↓
Frontend (Chat UI)
    ↓
Backend API (localhost:5001)
    ↓
Intent Classifier (Groq LLM)
    ↓
GraphQL Client (via VPN)
    ↓
Response Generator (Groq LLM)
    ↓
Frontend (Display + Charts)
```

## 🎉 Enjoy Your Demo!

Everything is set up and ready. Open `http://localhost:8080` and start asking questions!

