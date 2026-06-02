# MongoDB Setup Guide

## Overview
The system now automatically saves all processed CVs to MongoDB Atlas. You can retrieve and filter candidates by domain, sub-domain, date, and score.

## Setup Steps

### 1. Get MongoDB Atlas Connection String

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster (or use existing)
3. Go to "Database Access" → Create a database user
4. Go to "Network Access" → Add your IP (or 0.0.0.0/0 for development)
5. Go to "Database" → Click "Connect" → Choose "Connect your application"
6. Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=cv_shortlisting
MONGODB_ENABLED=true
```

**Important**: Replace `username` and `password` with your actual MongoDB Atlas credentials.

### 3. Initialize Indexes

After starting the server, call this endpoint once to create indexes:

```bash
POST http://localhost:8000/api/candidates/init-indexes
```

Or visit: `http://localhost:8000/api/candidates/init-indexes` in your browser.

Indexes are also created automatically on server startup.

## How It Works

### Automatic Saving

When you score a CV via `/api/cv/score`, it automatically saves to MongoDB:
- **Name** and **Phone** (for identification)
- **Primary Domain** and **Sub-Domain** (for filtering)
- **Score** (only for Jewellery Retail candidates)
- **Full Profile** (complete parsed data)
- **Checked Date** (for filtering old CVs)

### Retrieving Candidates

#### List All Candidates
```bash
GET http://localhost:8000/api/candidates
```

#### Filter by Domain
```bash
GET http://localhost:8000/api/candidates?domain=Jewellery%20Retail
```

#### Filter by Sub-Domain
```bash
GET http://localhost:8000/api/candidates?sub_domain=Sales%20Executive
```

#### Filter by Score (Jewellery Retail only)
```bash
GET http://localhost:8000/api/candidates?domain=Jewellery%20Retail&min_score=50
```

#### Filter by Date Range
```bash
# CVs checked after 2025-01-01
GET http://localhost:8000/api/candidates?date_from=2025-01-01

# CVs checked between dates
GET http://localhost:8000/api/candidates?date_from=2025-01-01&date_to=2025-01-31
```

#### Combined Filters
```bash
GET http://localhost:8000/api/candidates?domain=Jewellery%20Retail&min_score=70&date_from=2025-01-01&limit=20
```

#### Pagination
```bash
# First page (50 results)
GET http://localhost:8000/api/candidates?skip=0&limit=50

# Second page
GET http://localhost:8000/api/candidates?skip=50&limit=50
```

### Get Single Candidate Details

```bash
GET http://localhost:8000/api/candidates/{candidate_id}
```

Returns full candidate document including complete profile.

## Response Format

### List Response
```json
{
  "total": 150,
  "limit": 50,
  "skip": 0,
  "candidates": [
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j0k1",
      "full_name": "BIBINA JOHNSON",
      "phone": "+971 564212136",
      "primary_domain": "General Retail",
      "sub_domain": "Cashier & Sales Executive",
      "checked_date": "2025-01-20T10:30:00Z",
      "score": null
    },
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j0k2",
      "full_name": "ASAD MADANI",
      "phone": "+971588522846",
      "primary_domain": "Jewellery Retail",
      "sub_domain": "Sales Executive",
      "checked_date": "2025-01-19T14:20:00Z",
      "score": {
        "total_score": 43,
        "candidate_category": "Eligible Candidate",
        "breakdown": {...},
        "strengths": [...]
      }
    }
  ]
}
```

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `domain` | string | Filter by primary domain | `Jewellery Retail` |
| `sub_domain` | string | Filter by sub-domain | `Sales Executive` |
| `min_score` | integer | Minimum score (Jewellery only) | `50` |
| `date_from` | ISO date | CVs checked after this date | `2025-01-01` |
| `date_to` | ISO date | CVs checked before this date | `2025-01-31` |
| `limit` | integer | Results per page (1-100) | `50` |
| `skip` | integer | Pagination offset | `0` |
| `sort_by` | string | Field to sort by | `checked_date` |
| `sort_order` | string | `asc` or `desc` | `desc` |

## Database Schema

See `MONGODB_ARCHITECTURE.md` for detailed schema documentation.

## Notes

- MongoDB is **optional** - the system works without it, but won't save candidates
- If MongoDB is not configured, scoring still works but candidates won't be saved
- All dates are stored in UTC
- Indexes are created automatically for performance
- The `checked_date` field allows filtering out old CVs

