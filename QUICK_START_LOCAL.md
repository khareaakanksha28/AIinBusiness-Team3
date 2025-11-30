# Quick Start - Local Mac Setup 🚀

Run FactoryTwin AI completely locally on your Mac - **FREE and simple!**

## 3 Simple Steps

### 1. Get Groq API Key (Free)

1. Go to https://console.groq.com/
2. Sign up (free account)
3. Create API key
4. Copy it

### 2. Configure

Edit `local_config.sh` and add your API key:

```bash
export GROQ_API_KEY="gsk_your_actual_key_here"
```

### 3. Run

```bash
# Make sure VPN is connected!
./run_local.sh
```

That's it! Server runs on `http://localhost:5000`

## Test It

In another terminal:

```bash
./test_local.sh
```

Or manually:

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the revenue from my total firm orders?"}'
```

## What You Get

- ✅ **Free**: No AWS costs
- ✅ **Fast**: Direct VPN connection
- ✅ **Simple**: Everything local
- ✅ **Easy**: Just run one script

## Troubleshooting

**"Cannot reach GraphQL API"**
→ Make sure VPN is connected

**"Module not found"**
→ Run: `pip install -r requirements-local.txt`

**"Groq API error"**
→ Check your API key in `local_config.sh`

## Next Steps

- Update frontend to use `http://localhost:5000/query`
- Develop and test locally
- Deploy to AWS later when ready

Enjoy! 🎉

