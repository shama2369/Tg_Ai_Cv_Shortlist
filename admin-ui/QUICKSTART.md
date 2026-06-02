# Quick Start Guide

## Prerequisites

1. **FastAPI backend must be running** on `http://127.0.0.1:8000`
2. **Node.js and npm** installed

## Setup Steps

### 1. Install Dependencies

```bash
cd admin-ui
npm install
```

### 2. Create `.env` File

Create `admin-ui/.env` with:

```env
VITE_API_BASE=http://127.0.0.1:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The UI will automatically open at http://localhost:5173

## Usage Flow

1. **Dashboard** → Click "New CV Upload"
2. **Upload** → Select PDF or image files
3. **Extract** → Click "1) Extract Text" to extract text from files
4. **Parse** → Click "2) Parse with AI" to extract structured data
5. **Score** → Click "3) Score" to calculate candidate score

## Troubleshooting

### CORS Errors
- Make sure FastAPI backend has CORS middleware enabled (already added to `app/main.py`)
- Verify backend is running on `http://127.0.0.1:8000`

### API Connection Issues
- Check `.env` file has correct `VITE_API_BASE` URL
- Verify FastAPI server is running: `http://127.0.0.1:8000/health`

### Port Already in Use
- Change port in `vite.config.js` if 5173 is taken
- Update CORS origins in `app/main.py` if using different port

