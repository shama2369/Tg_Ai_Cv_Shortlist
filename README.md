# AI CV Shortlisting System

FastAPI-based application for extracting and scoring CVs/resumes for jewellery retail hiring.

## Setup

### 1. Install Dependencies

Make sure you have Python 3.8+ installed. Then:

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key for AI extraction

**Optional (MongoDB):**
- `MONGODB_ENABLED` - Set to "true" if using MongoDB
- `MONGODB_URI` - MongoDB connection string
- `DB_NAME` - Database name (default: cv_shortlisting)

### 3. Run the Application

**Option 1: Using the run script (Windows)**
```bash
run.bat
```

**Option 2: Manual command**
```bash
# Activate virtual environment
venv\Scripts\activate

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 3: Python module**
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /health` - Check API status

### CV Upload
- `POST /api/cv/upload` - Upload CV files (validation only)

### Text Extraction
- `POST /api/cv/extract` - Extract text from PDF/images (with OCR fallback)

### AI Parsing
- `POST /api/cv/parse` - Extract structured data from CV text using AI

### Scoring
- `POST /api/cv/score` - Calculate shortlist score from structured profile

## Workflow

1. **Upload & Extract**: `POST /api/cv/extract` with PDF/image files
2. **Parse**: `POST /api/cv/parse` with extracted text
3. **Score**: `POST /api/cv/score` with parsed profile

## Requirements

- Python 3.8+
- OpenAI API key
- **Tesseract OCR** (for image OCR) - **Required for image processing**
- MongoDB (optional - only if storing candidates)

### Installing Tesseract OCR (Windows)

**For image OCR to work, you need to install Tesseract OCR separately:**

1. **Download Tesseract OCR:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the Windows installer (latest version)

2. **Install Tesseract:**
   - Run the installer
   - Default installation path: `C:\Program Files\Tesseract-OCR`
   - **Important:** During installation, check "Add to PATH" option

3. **Verify Installation:**
   ```bash
   tesseract --version
   ```

4. **If not in PATH, set environment variable:**
   - Add to your `.env` file:
   ```env
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```
   - Or set it in Windows Environment Variables

5. **Restart your application** after installation

**Note:** Tesseract OCR is separate from Python packages. Installing `pytesseract` via pip is not enough - you need the actual Tesseract OCR engine installed on your system.

## Notes

- CV files are processed in-memory and NOT stored
- Only extracted structured data can be stored (if MongoDB enabled)
- Mobile-first design for image uploads from phones

