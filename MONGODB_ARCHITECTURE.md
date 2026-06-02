# MongoDB Storage Architecture for CV Shortlisting

## Overview
Store processed CVs in MongoDB Atlas for retrieval, filtering, and management.

## Database Schema

### Collection: `candidates`

```json
{
  "_id": ObjectId("..."),
  "full_name": "BIBINA JOHNSON",
  "phone": "+971 564212136",
  "email": "bibinajohnson8@gmail.com",
  "primary_domain": "General Retail",
  "sub_domain": "Cashier & Sales Executive",
  "domain_confidence": 0.85,
  
  // Scoring data (only for Jewellery Retail)
  "score": {
    "total_score": 43,
    "candidate_category": "Eligible Candidate",
    "breakdown": {
      "age_preference": 0,
      "education": 4,
      "languages": 6,
      "skills": 0,
      "jewellery_experience": 33
    },
    "strengths": ["Jewellery Sales", "Marketing Orientation"]
  },
  
  // Profile data (full parsed profile)
  "profile": {
    "full_name": "...",
    "phone": "...",
    "nationality": "...",
    "languages": ["English", "Malayalam", "Hindi"],
    "age": 25,
    "education": {...},
    "experience": {...},
    "skills": {...},
    "certifications": [...]
  },
  
  // Metadata
  "checked_date": ISODate("2025-01-20T10:30:00Z"),
  "created_at": ISODate("2025-01-20T10:30:00Z"),
  "updated_at": ISODate("2025-01-20T10:30:00Z")
}
```

## Logic Flow

### 1. Save CV (After Scoring)
- When a CV is scored (via `/api/cv/score`), save to MongoDB
- Store: name, phone, domain, sub-domain, score (if jewellery), full profile, date
- Use `checked_date` for filtering old CVs

### 2. Retrieve Candidates

#### Endpoint: `GET /api/candidates`
Query parameters:
- `domain`: Filter by primary_domain (e.g., "Jewellery Retail", "General Retail")
- `sub_domain`: Filter by sub_domain (e.g., "Sales Executive", "Cashier")
- `min_score`: Minimum score (only for Jewellery Retail)
- `date_from`: Filter CVs checked after this date (ISO format)
- `date_to`: Filter CVs checked before this date (ISO format)
- `limit`: Number of results (default: 50)
- `skip`: Pagination offset (default: 0)

#### Response Format:
```json
{
  "total": 150,
  "limit": 50,
  "skip": 0,
  "candidates": [
    {
      "_id": "...",
      "full_name": "BIBINA JOHNSON",
      "phone": "+971 564212136",
      "primary_domain": "General Retail",
      "sub_domain": "Cashier & Sales Executive",
      "checked_date": "2025-01-20T10:30:00Z",
      "score": null  // Only for Jewellery Retail
    },
    {
      "_id": "...",
      "full_name": "ASAD MADANI",
      "phone": "+971588522846",
      "primary_domain": "Jewellery Retail",
      "sub_domain": "Sales Executive",
      "checked_date": "2025-01-19T14:20:00Z",
      "score": {
        "total_score": 43,
        "candidate_category": "Eligible Candidate"
      }
    }
  ]
}
```

### 3. Get Single Candidate Details
- `GET /api/candidates/{candidate_id}`: Get full candidate details including full profile

### 4. Indexes for Performance
- Index on `primary_domain`
- Index on `sub_domain`
- Index on `checked_date` (for date filtering)
- Compound index on `(primary_domain, sub_domain)`
- Index on `score.total_score` (for jewellery filtering)

## Implementation Steps

1. Create MongoDB document model (`app/models/candidate.py`)
2. Create database service (`app/services/candidate_db.py`)
3. Update score endpoint to save to DB
4. Create candidate retrieval endpoints (`app/api/candidates.py`)
5. Add indexes for performance

## Environment Variables

Add to `.env`:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=cv_shortlisting
MONGODB_ENABLED=true
```

