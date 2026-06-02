# CV Score Endpoint Response Explanation

## Overview

The `/api/cv/score` endpoint returns the **same response structure** whether called:
1. **Directly** (backend alone via curl/Postman/API client)
2. **Through the frontend** (React admin UI)

The only difference is **how the response is handled and displayed**.

---

## Backend Response Structure

When you call `POST /api/cv/score` with a valid profile, the backend returns:

```json
{
  "status": "scored",
  "total_score": 43,
  "breakdown": {
    "age_preference": 0,
    "education": 4,
    "languages": 6,
    "skills": 0,
    "jewellery_experience": 33
  },
  "breakdown_details": {
    "age": {
      "age": 37,
      "flags": ["Age 36+"]
    },
    "education": {
      "diploma_or_degree": 7
    },
    "languages": {
      "languages_counted": ["english", "hindi", "kannada"],
      "raw_points": 6,
      "cap": 20
    },
    "skills": {},
    "jewellery_experience": {
      "region_used": "uae",
      "jewellery_years_used": 8,
      "base_points": 28,
      "marketing_facing_jewellery_bonus": 5
    }
  },
  "strengths": [
    "Jewellery Sales",
    "Marketing Orientation"
  ],
  "visa_info": {
    "visa_type": "Unknown",
    "visa_expiry_date": null,
    "included_in_score": false
  },
  "note": "Deterministic scoring (v3). Visa is reported only and excluded from score."
}
```

### Response Fields Explained

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always `"scored"` when successful |
| `total_score` | integer | Sum of all category scores (0-100+) |
| `breakdown` | object | Points per category (summary) |
| `breakdown_details` | object | Detailed scoring breakdown with metadata |
| `strengths` | array | Qualitative strengths identified |
| `visa_info` | object | Visa information (NOT included in score) |
| `note` | string | Informational note about scoring |

---

## Scenario 1: Backend Alone (Direct API Call)

### Example: Using curl

```bash
curl -X POST "http://127.0.0.1:8000/api/cv/score" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "full_name": "John Doe",
      "age": 28,
      "experience": {
        "total_years": 5,
        "jewellery_years": 3,
        "jewellery_countries": ["UAE"],
        "has_jewellery_experience": true
      },
      "education": {
        "diploma_or_degree": true
      },
      "languages": ["English", "Hindi"],
      "skills": {},
      "visa": {}
    }
  }'
```

### Response Handling

- **Raw JSON response** - You see the complete JSON structure
- **No transformation** - Data is exactly as returned by `score_candidate()`
- **Manual parsing** - You need to parse and display it yourself

### What You See

```json
{
  "status": "scored",
  "total_score": 45,
  "breakdown": {...},
  "breakdown_details": {...},
  "strengths": [...],
  "visa_info": {...},
  "note": "..."
}
```

---

## Scenario 2: Frontend (React Admin UI)

### Flow

1. **User clicks "3) Score" button** in `UploadFlow.jsx`
2. **Frontend calls** `scoreProfile(parseRes.profile)` from `cvApi.js`
3. **Axios sends POST request** to `/api/cv/score`
4. **Backend processes** and returns the same JSON structure
5. **Frontend receives** response in `scoreRes` state
6. **ScoreViewer component** displays the data

### Code Flow

```javascript
// admin-ui/src/pages/UploadFlow.jsx
async function onScore() {
  const data = await scoreProfile(parseRes.profile);
  setScoreRes(data);  // Stores the full response
}

// admin-ui/src/components/ScoreViewer.jsx
export default function ScoreViewer({ report }) {
  const { total_score, breakdown, strengths, visa_info, breakdown_details } = report;
  // Displays formatted UI
}
```

### Response Handling

- **Same JSON structure** - Frontend receives identical data
- **Automatic parsing** - Axios automatically parses JSON
- **Formatted display** - `ScoreViewer` component formats it for UI

### What You See in UI

```
Score Report
Total Score: 43

Breakdown
  • age_preference: 0
  • education: 4
  • languages: 6
  • skills: 0
  • jewellery_experience: 33

Strengths
  • Jewellery Sales
  • Marketing Orientation

Visa (not scored)
  Type: Unknown
  Expiry: (none)

[Debug details ▼]
  (expandable JSON view)
```

---

## Key Differences Summary

| Aspect | Backend Alone | Frontend |
|--------|---------------|----------|
| **Response Structure** | ✅ Same | ✅ Same |
| **Data Format** | Raw JSON | Parsed JavaScript object |
| **Display** | Manual (you format it) | Automatic (React component) |
| **Error Handling** | Manual | Automatic (shown in UI) |
| **User Experience** | Developer-friendly | End-user friendly |

---

## Response Structure Details

### `breakdown` (Summary)

Quick reference of points per category:

```json
{
  "age_preference": 0,
  "education": 4,
  "languages": 6,
  "skills": 0,
  "jewellery_experience": 33
}
```

### `breakdown_details` (Detailed)

Contains metadata and flags:

```json
{
  "age": {
    "age": 37,
    "flags": ["Age 36+"]
  },
  "education": {
    "diploma_or_degree": 7
  },
  "languages": {
    "languages_counted": ["english", "hindi"],
    "raw_points": 4,
    "cap": 20
  },
  "jewellery_experience": {
    "region_used": "uae",
    "jewellery_years_used": 8,
    "base_points": 28,
    "marketing_facing_jewellery_bonus": 5
  }
}
```

### `strengths` (Array)

Qualitative strengths identified:

```json
["Jewellery Sales", "Marketing Orientation"]
```

### `visa_info` (Object)

Visa information (NOT scored):

```json
{
  "visa_type": "Visit" | "Employment" | "Cancelled" | "Unknown",
  "visa_expiry_date": "2024-12-31" | null,
  "days_remaining": 45 | undefined,  // Only for Visit visas
  "included_in_score": false  // Always false
}
```

---

## Testing Both Scenarios

### Test Backend Directly

```bash
# 1. Get a parsed profile first
curl -X POST "http://127.0.0.1:8000/api/cv/parse" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your CV text here..."}'

# 2. Use the profile from step 1
curl -X POST "http://127.0.0.1:8000/api/cv/score" \
  -H "Content-Type: application/json" \
  -d '{"profile": {...profile from step 1...}}'
```

### Test Through Frontend

1. Open `http://localhost:5173`
2. Upload CV → Extract → Parse → Score
3. View the formatted score report in the UI
4. Check browser DevTools → Network tab to see raw response

---

## Important Notes

1. **Same Response**: Both methods return identical JSON structure
2. **No Transformation**: Frontend doesn't modify the response, only displays it
3. **Error Handling**: Both return HTTP errors in same format:
   ```json
   {
     "detail": "Error message here"
   }
   ```
4. **Status Codes**:
   - `200` - Success
   - `422` - Validation error (invalid profile)
   - `500` - Server error

---

## Debugging

### Check Raw Response (Frontend)

```javascript
// In browser console after scoring
console.log(scoreRes);
```

### Check Backend Logs

The backend logs errors but not successful responses by default. Add logging if needed:

```python
logger.info(f"Score response: {report}")
```

