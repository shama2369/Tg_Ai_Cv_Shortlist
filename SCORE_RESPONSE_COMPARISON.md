# Score Endpoint: Backend vs Frontend Comparison

## Quick Answer

**The response is IDENTICAL in both cases.** The only difference is how it's displayed.

---

## Visual Comparison

### Backend Response (Raw JSON)

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
    "age": {"age": 37, "flags": ["Age 36+"]},
    "education": {"diploma_or_degree": 7},
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
  "strengths": ["Jewellery Sales", "Marketing Orientation"],
  "visa_info": {
    "visa_type": "Unknown",
    "visa_expiry_date": null,
    "included_in_score": false
  },
  "note": "Deterministic scoring (v3). Visa is reported only and excluded from score."
}
```

### Frontend Display (Formatted UI)

```
┌─────────────────────────────────────┐
│ Score Report                        │
├─────────────────────────────────────┤
│ Total Score: 43                    │
│                                     │
│ Breakdown                          │
│   • age_preference: 0               │
│   • education: 4                   │
│   • languages: 6                   │
│   • skills: 0                      │
│   • jewellery_experience: 33       │
│                                     │
│ Strengths                          │
│   • Jewellery Sales                │
│   • Marketing Orientation         │
│                                     │
│ Visa (not scored)                  │
│   Type: Unknown                    │
│                                     │
│ ▼ Debug details                    │
│   {JSON details...}                │
└─────────────────────────────────────┘
```

---

## Code Flow Comparison

### Backend Direct Call

```python
# app/api/score.py
@router.post("/score")
def score_cv(req: ScoreRequest):
    profile_dict = req.profile.model_dump()
    report = score_candidate(profile_dict, today=date.today())
    return report  # Returns dict directly → FastAPI serializes to JSON
```

**Result**: HTTP response with JSON body

### Frontend Call

```javascript
// admin-ui/src/api/cvApi.js
export async function scoreProfile(profile) {
  const res = await api.post("/api/cv/score", { profile });
  return res.data;  // Axios automatically parses JSON → JavaScript object
}

// admin-ui/src/pages/UploadFlow.jsx
const data = await scoreProfile(parseRes.profile);
setScoreRes(data);  // Stores JavaScript object

// admin-ui/src/components/ScoreViewer.jsx
const { total_score, breakdown, strengths } = report;  // Destructures object
// Renders formatted UI
```

**Result**: JavaScript object displayed in React component

---

## Data Flow Diagram

### Backend Alone
```
[Your Code/curl]
    ↓ POST /api/cv/score
[FastAPI Endpoint]
    ↓ score_candidate()
[Scoring Engine]
    ↓ Returns dict
[FastAPI Serialization]
    ↓ JSON.stringify()
[HTTP Response]
    ↓ Raw JSON
[You see JSON]
```

### Frontend
```
[React Component]
    ↓ scoreProfile()
[Axios HTTP Client]
    ↓ POST /api/cv/score
[FastAPI Endpoint]
    ↓ score_candidate()
[Scoring Engine]
    ↓ Returns dict
[FastAPI Serialization]
    ↓ JSON.stringify()
[HTTP Response]
    ↓ JSON.parse() (automatic)
[JavaScript Object]
    ↓ setScoreRes()
[React State]
    ↓ <ScoreViewer report={scoreRes} />
[Formatted UI]
```

---

## Key Points

1. **Same Backend Logic**: Both use the exact same `score_candidate()` function
2. **Same Response Structure**: Identical JSON structure returned
3. **Different Presentation**: 
   - Backend: Raw JSON (for developers)
   - Frontend: Formatted UI (for end users)
4. **No Data Loss**: Frontend displays all the same information, just formatted

---

## Example: Same Profile, Same Score

### Input Profile
```json
{
  "age": 28,
  "education": {"diploma_or_degree": true},
  "languages": ["English", "Hindi"],
  "experience": {
    "jewellery_years": 3,
    "jewellery_countries": ["UAE"]
  }
}
```

### Backend Response (Both Cases)
```json
{
  "total_score": 45,
  "breakdown": {
    "age_preference": 10,
    "education": 7,
    "languages": 4,
    "skills": 0,
    "jewellery_experience": 24
  }
}
```

**Result**: Same score (45) regardless of how you call it!

---

## Why This Matters

- **Consistency**: Same scoring logic everywhere
- **Debugging**: Test backend directly without frontend
- **API Usage**: Other clients can use the same endpoint
- **Reliability**: Frontend doesn't modify scores, just displays them

