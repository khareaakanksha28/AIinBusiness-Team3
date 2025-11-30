# GraphQL API Response Structure

## Working Query Example

Your direct query that works:
```graphql
{
  simulation(identifier: "4c386d0a-0133-4a66-aee0-1a8178ddabb1") {
    charts {
      demandByFulfillmentDonut(
        from: "2025-01-01T00:00:00Z"
        until: "2025-11-27T00:00:00Z"
        sites: []
        onTimeDeliveryBuffer: 0.0
      ) {
        stackDataList { name value }
      }
    }
  }
}
```

## Response Structure

```json
{
  "data": {
    "simulation": {
      "charts": {
        "demandByFulfillmentDonut": {
          "stackDataList": [
            {
              "name": "Firm Order",
              "value": 422132.05999999953
            }
          ]
        }
      }
    }
  }
}
```

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

