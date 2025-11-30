# Starting the Local Server

## ✅ VPN Status: Connected
Your WireGuard VPN is running and GraphQL API is reachable!

## Next Step: Set Groq API Key

The server needs a Groq API key for the LLM (Intent Classifier & Response Generator).

### Option 1: Quick Setup (Temporary)
```bash
export GROQ_API_KEY="your-actual-key-here"
./run_local.sh
```

### Option 2: Permanent Setup
1. Get free API key from https://console.groq.com/
2. Edit `local_config.sh`:
   ```bash
   export GROQ_API_KEY="gsk_your_actual_key_here"
   ```
3. Run:
   ```bash
   ./run_local.sh
   ```

## Once Started

The server will run on: **http://localhost:5000**

### Test it:
```bash
# In another terminal
./test_local.sh

# Or manually:
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the revenue from my total firm orders?"}'
```

## Ready to Start?

Just run:
```bash
./run_local.sh
```

The script will:
1. ✅ Check VPN connectivity (already working!)
2. ✅ Set up Python environment
3. ✅ Install dependencies
4. ✅ Start the server

Press Ctrl+C to stop when done.

