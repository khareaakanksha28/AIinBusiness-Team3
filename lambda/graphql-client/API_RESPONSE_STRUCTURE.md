# GraphQL API Response Structure


## Lambda Query Structure

The Lambda requests additional fields for compatibility:
- `startDate` - Optional, may be null
- `stackDataList.name` - ✅ Always present
- `stackDataList.value` - ✅ Always present  
- `stackDataList.quantity` - Optional, may be null

The Lambda will work correctly even if `startDate` or `quantity` are null, as long as `name` and `value` are present in `stackDataList`.

## Expected Lambda Response

When Lambda calls the API, it will receive:
```json
{
  "statusCode": 200,
  "endpoint": "demandByFulfillmentDonut",
  "data": {
    "startDate": "2025-01-01T00:00:00Z" | null,
    "stackDataList": [
      {
        "name": "Firm Order",
        "value": 422132.05999999953,
        "quantity": null | <number>
      }
    ]
  }
}
```

## Testing

The Lambda is configured to:
1. Request all fields (including optional ones)
2. Handle null/optional fields gracefully
3. Extract `stackDataList` with `name` and `value` (required fields)

Your API response structure is compatible with the Lambda's expectations.

