# GraphQL Schema Updates

## Updated Endpoint: demandByFulfillmentDonut

### Schema Compliance

The query has been updated to match the exact GraphQL schema:

**Parameters:**
- ✅ `from: Instant!` - Start date
- ✅ `until: Instant!` - End date  
- ✅ `sites: [UUID!]!` - Site identifiers (empty = all sites)
- ✅ `onTimeDeliveryBuffer: Float!` - Buffer value
- ✅ `useProjectedCompletion: Boolean` - **NEW** Optional parameter

### Response Structure

The endpoint returns `ProjectedDemandDataObject` with:

```typescript
{
  startDate: Instant
  stackDataList: [
    {
      name: String      // "Overdue", "Forecasted", "Firm Order"
      quantity: Float
      value: Float
    }
  ]
}
```

### Example Responses

**All Sites (empty sites array):**
```json
[
  { "name": "Overdue", "quantity": 149, "value": 1079098.66 },
  { "name": "Forecasted", "quantity": 2316, "value": 14611009.21 },
  { "name": "Firm Order", "quantity": 4848, "value": 32595400.38 }
]
```

**Minneapolis Site:**
```json
[
  { "name": "Overdue", "quantity": 39, "value": 748409.70 },
  { "name": "Forecasted", "quantity": 643, "value": 10819388.33 },
  { "name": "Firm Order", "quantity": 1381, "value": 24186824.79 }
]
```

**St. Cloud Site:**
```json
[
  { "name": "Overdue", "quantity": 110, "value": 330688.96 },
  { "name": "Forecasted", "quantity": 1673, "value": 3791620.88 },
  { "name": "Firm Order", "quantity": 3467, "value": 8408575.59 }
]
```

## Implementation Notes

1. **Optional Parameters**: The `useProjectedCompletion` parameter is optional and omitted if `None`
2. **Site Filtering**: Currently using empty array `[]` for all sites
3. **Type Safety**: All types match the schema exactly (`Instant!`, `UUID!`, `Float!`)

## Future Enhancements

Potential features to add:
- Site selection UI in frontend
- Toggle for `useProjectedCompletion`
- Date range picker
- Buffer value adjustment

