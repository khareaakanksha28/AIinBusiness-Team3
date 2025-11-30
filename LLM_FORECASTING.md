# LLM-Based Demand Forecasting

## Overview

The system now uses **Groq LLM to predict Forecasted demand** based on available Firm Order data.

## How It Works

### Flow:
1. **Get Firm Order Data** from GraphQL API
2. **Check for Forecasted Data** - if missing or zero
3. **Use Groq LLM** to analyze Firm Order patterns
4. **Predict Forecasted** demand based on:
   - Historical patterns (typically 2-4x Firm Order value)
   - Industry standards
   - Manufacturing trends
5. **Add Predicted Data** to chart visualization

### LLM Prompt:
The LLM receives:
- Firm Order value and quantity
- Instructions to predict based on typical patterns
- Request for JSON response with predicted values

### Prediction Logic:
- **Forecasted Value**: Typically 2-4x Firm Order value
- **Forecasted Quantity**: Usually 1.5-3x Firm Order quantity
- **Fallback**: If LLM fails, uses 3x multiplier for value, 2.5x for quantity

## Example

**Input (Firm Order):**
- Value: $3,377,056.48
- Quantity: 13,952 units

**LLM Prediction (Forecasted):**
- Value: $10,741,221.92 (~3.2x)
- Quantity: 41,958 units (~3x)

**Chart Shows:**
- Firm Order: Medium blue segment
- Forecasted: Gray segment (predicted)
- Total in center: 55,910 units

## Benefits

✅ **Intelligent Prediction**: Uses LLM reasoning, not just multipliers
✅ **Context-Aware**: Considers manufacturing patterns
✅ **Automatic**: No manual configuration needed
✅ **Visual**: Shows predicted data in chart

## Configuration

The prediction uses:
- **Model**: `llama-3.3-70b-versatile` (configurable via `GROQ_MODEL`)
- **Temperature**: 0.3 (for consistent predictions)
- **Max Tokens**: 200

## Future Enhancements

Potential improvements:
- Use historical data for better predictions
- Consider seasonal trends
- Factor in market conditions
- Learn from actual vs predicted accuracy

