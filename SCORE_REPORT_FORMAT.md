# Score Report Format

## New Report Structure

The score report now follows this format:

### 1. Header Section
- **First Name**: Extracted from the candidate's full name
- **Total Score**: Overall score (0-100+)
- **Candidate Category**: Based on score thresholds:
  - **≥ 80**: "Prospective Candidate" (Green badge)
  - **≥ 70**: "Good Candidate" (Blue badge)
  - **≥ 50**: "Eligible Candidate" (Amber badge)
  - **< 50**: "Not Eligible" (Red badge)

### 2. Detailed Segments Section
Each segment shows:
- **Score**: Points awarded for this segment
- **Details**: Key information extracted from parsed data
- **Flags**: Any warnings or flags (e.g., "Age 36+")

Segments include:
- **Age**: Age value, score, and any flags
- **Education**: Education level and score
- **Languages**: Languages spoken, count, and score
- **Skills**: Relevant skills identified and score
- **Jewellery Experience**: Years of experience, countries, region, and score

### 3. Score Breakdown with Pie Chart
- **Visual Pie Chart**: Shows percentage distribution of scores
- **Breakdown List**: Detailed list with color-coded categories:
  - Age Preference (Purple)
  - Education (Green)
  - Languages (Yellow)
  - Skills (Orange)
  - Jewellery Experience (Teal)

### 4. Strengths Section
- Lists qualitative strengths identified (e.g., "Jewellery Sales", "Marketing Orientation")

### 5. Visa Information Section
- Visa type, expiry date, and days remaining (if applicable)
- Note: Visa is NOT included in the score

## Backend Changes

### New Fields in Response

```json
{
  "first_name": "John",
  "total_score": 75,
  "candidate_category": "Good Candidate",
  "segment_details": {
    "age": {
      "value": 28,
      "score": 10,
      "flags": [],
      "details": "Age: 28 years"
    },
    "education": {
      "level": "Diploma/Degree",
      "score": 7,
      "details": "Education: Diploma/Degree"
    },
    "languages": {
      "count": 3,
      "languages": ["english", "hindi", "kannada"],
      "score": 6,
      "details": "Languages: English, Hindi, Kannada"
    },
    "skills": {
      "items": ["Digital Marketing", "UAE Driving License"],
      "score": 10,
      "details": "Skills: Digital Marketing, UAE Driving License"
    },
    "jewellery_experience": {
      "years": 5,
      "countries": ["UAE"],
      "region": "UAE",
      "score": 42,
      "details": "Jewellery Experience: 5 years in UAE"
    }
  }
}
```

## Frontend Changes

### New Components
- **Enhanced ScoreViewer**: Displays new format with pie chart
- **Pie Chart Visualization**: Using Recharts library
- **Category Badges**: Color-coded candidate categories
- **Segment Cards**: Detailed information cards for each scoring segment

### Installation Required

```bash
cd admin-ui
npm install recharts
```

## Example Output

```
┌─────────────────────────────────────────┐
│ John                                    │
│ Total Score: 75                         │
│ [Good Candidate]                        │
├─────────────────────────────────────────┤
│ Detailed Segments                       │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │ Age     │ │Education│ │Languages│   │
│ │ 10 pts  │ │ 7 pts   │ │ 6 pts   │   │
│ │ Age: 28 │ │Degree   │ │3 langs  │   │
│ └─────────┘ └─────────┘ └─────────┘   │
├─────────────────────────────────────────┤
│ Score Breakdown                         │
│ [Pie Chart]    [Breakdown List]         │
├─────────────────────────────────────────┤
│ Strengths                                │
│ [Jewellery Sales] [Marketing Orientation]│
└─────────────────────────────────────────┘
```

## Score Thresholds

| Score Range | Category | Color |
|-------------|----------|-------|
| ≥ 80 | Prospective Candidate | Green |
| 70-79 | Good Candidate | Blue |
| 50-69 | Eligible Candidate | Amber |
| < 50 | Not Eligible | Red |

