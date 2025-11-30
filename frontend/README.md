# FactoryTwin AI Frontend

A modern chat interface with data visualizations for FactoryTwin AI.

## Features

- 💬 Interactive chat interface
- 📊 Dynamic chart visualizations (Donut & Bar charts)
- 🎨 Modern, responsive UI
- ⚡ Real-time responses from local server

## Quick Start

### 1. Make sure the local server is running

```bash
cd ~/factorytwin-ai
./run_local.sh
```

The server should be running on `http://localhost:5001`

### 2. Open the frontend

Simply open `index.html` in your browser:

```bash
cd ~/factorytwin-ai/frontend
open index.html
```

Or use a local server:

```bash
# Python 3
python3 -m http.server 8080

# Then open: http://localhost:8080
```

### 3. Start chatting!

- Click example questions or type your own
- See responses with visualizations
- Charts update automatically based on data type

## File Structure

```
frontend/
├── index.html      # Main HTML file
├── styles.css      # Styling
├── app.js          # JavaScript logic
└── README.md       # This file
```

## API Integration

The frontend connects to:
- **API URL**: `http://localhost:5001/query`
- **Health Check**: `http://localhost:5001/health`

## Chart Types

### Donut Chart
- Used for: Total demand breakdown (Firm Orders, Overdue, Forecasted)
- Shows: Proportional values with percentages

### Stacked Bar Chart
- Used for: Monthly/historical data
- Shows: Time series with stacked categories

## Customization

### Change API URL
Edit `app.js`:
```javascript
const API_URL = 'http://localhost:5001/query';
```

### Modify Colors
Edit `generateColors()` function in `app.js`

### Adjust Styling
Edit `styles.css` - all colors are in CSS variables at the top

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Modern mobile browsers

## Troubleshooting

**Charts not showing?**
- Check browser console for errors
- Verify server is running
- Check that chart data is in the response

**Cannot connect to server?**
- Make sure local server is running: `./run_local.sh`
- Check server is on port 5001
- Verify VPN is connected (for GraphQL API)

**CORS errors?**
- The local server has CORS enabled
- If issues persist, check server logs

