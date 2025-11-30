# Quick Restart Guide

When you're ready to continue, here's how to restart everything:

## Start Backend Server

```bash
cd ~/factorytwin-ai
source local_config.sh
# GROQ_API_KEY should be set in local_config.sh
python3 local_server.py
```

Or use the script:
```bash
./run_local.sh
```

## Start Frontend Server

In a new terminal:
```bash
cd ~/factorytwin-ai/frontend
python3 -m http.server 8080
```

## Access

- Frontend: http://localhost:8080
- Backend API: http://localhost:5001/query
- Health Check: http://localhost:5001/health

## Current Status

✅ All code is saved and ready
✅ Configuration is set up
✅ VPN connection working
✅ GraphQL API accessible

Just restart the servers when ready!

