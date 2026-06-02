# CV Shortlisting Admin UI

React + Vite admin interface for the AI CV Shortlisting System.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure API URL

Create a `.env` file (or copy from `.env.example`):

```env
VITE_API_BASE=http://127.0.0.1:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The UI will open at http://localhost:5173

## Features

- **Upload Flow**: Upload PDF/images → Extract text → Parse with AI → Score candidate
- **Dashboard**: Quick access to upload new CVs
- **Real-time API Integration**: Connects to FastAPI backend at `/api/cv/*` endpoints

## API Endpoints Used

- `POST /api/cv/extract` - Extract text from PDF/images
- `POST /api/cv/parse` - Parse CV text with AI
- `POST /api/cv/score` - Score candidate profile

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

