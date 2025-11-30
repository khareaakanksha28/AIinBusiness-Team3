# Interactive Chat Flow

## 🎯 New Interactive Features

The chat interface now starts with a greeting and simulation selection!

## Flow

1. **Initial Greeting**
   - When the page loads, automatically sends "hello"
   - Backend responds with greeting and list of available simulations

2. **Simulation Selection**
   - User sees list of available simulations
   - Each simulation shows name and identifier
   - Click to select a simulation

3. **Ask Questions**
   - After selecting a simulation, user can ask questions
   - All queries use the selected simulation ID
   - Charts and responses are specific to that simulation

## Example Flow

```
User opens page
    ↓
Auto-sends "hello"
    ↓
Backend: "Hello! 👋 I'm FactoryTwin AI..."
    ↓
Shows simulation list:
  - Baseline (421ec61b...)
  - Baseline (4c386d0a...)
  - Baseline (acf86b6f...)
  ...
    ↓
User clicks a simulation
    ↓
System: "✅ Selected: Baseline"
    ↓
User asks: "What is the revenue from my total firm orders?"
    ↓
System responds with answer + chart
```

## API Changes

### Greeting Request
```json
POST /query
{
  "question": "hello"
}
```

### Greeting Response
```json
{
  "type": "greeting",
  "message": "Hello! 👋 I'm FactoryTwin AI...",
  "simulations": [
    {
      "identifier": "4c386d0a-0133-4a66-aee0-1a8178ddabb1",
      "name": "Baseline"
    },
    ...
  ]
}
```

### Question with Simulation
```json
POST /query
{
  "question": "What is the revenue from my total firm orders?",
  "simulation_id": "4c386d0a-0133-4a66-aee0-1a8178ddabb1"
}
```

## Frontend Features

- ✅ Auto-greeting on page load
- ✅ Interactive simulation selection buttons
- ✅ Visual confirmation when simulation is selected
- ✅ Prevents questions without simulation selection
- ✅ Shows example questions after selection

## Try It!

1. Open `http://localhost:8080`
2. Wait for automatic greeting
3. Click a simulation to select it
4. Ask questions about that simulation!

