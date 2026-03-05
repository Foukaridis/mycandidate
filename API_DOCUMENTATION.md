# API Documentation

## Candidates API

### Get Ward Candidates

Returns a JSON array of all candidates standing for election in the specified ward.

**URL** : `/api/v1/wards/<ward_id>/candidates`

**Method** : `GET`

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ward_id` | `string` | The ID of the ward to retrieve candidates for. |

**Success Response**

**Code** : `200 OK`

**Content example**

```json
[
  {
    "candidate_type": "ward",
    "locator": ["ward_id", "name"],
    "ward_id": "12345",
    "name": "John Candidate",
    "party": "Example Party",
    "orderno": "1"
  }
]
```

**Notes**

- The fields returned in the JSON objects depend on the columns available in the `candidates` table for the 'ward' candidate type.
- If no candidates are found for the given `ward_id`, an empty array `[]` is returned.
