# How to Start the Frontend

## Quick Start

### Step 1: Open Terminal
Open a terminal/command prompt in the project root directory.

### Step 2: Navigate to Admin UI
```bash
cd admin-ui
```

### Step 3: Install Dependencies (First Time Only)
```bash
npm install
```

### Step 4: Start Development Server
```bash
npm run dev
```

The frontend will start and automatically open at:
**http://localhost:5173**

---

## Prerequisites

1. **Node.js installed** (v16 or higher)
   - Check: `node --version`
   - Download: https://nodejs.org/

2. **Backend running** (FastAPI on port 8000)
   - Make sure your FastAPI backend is running
   - Test: http://127.0.0.1:8000/health

3. **Environment file** (optional)
   - Create `admin-ui/.env` if needed:
   ```env
   VITE_API_BASE=http://127.0.0.1:8000
   ```

---

## Windows PowerShell Commands

```powershell
# Navigate to admin-ui folder
cd admin-ui

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

---

## What You'll See

After running `npm run dev`:
- Terminal will show: `Local: http://localhost:5173/`
- Browser should auto-open
- You'll see the **TrichyGold CV Shortlisting** interface

---

## Troubleshooting

### Port 5173 Already in Use
```bash
# Kill the process using port 5173, or
# Edit vite.config.js to use a different port
```

### Module Not Found Errors
```bash
# Delete node_modules and reinstall
rm -rf node_modules
npm install
```

### Backend Connection Issues
- Verify backend is running: `http://127.0.0.1:8000/health`
- Check `.env` file has correct API URL
- Ensure CORS is enabled in FastAPI (already configured)

---

## Stop the Server

Press `Ctrl + C` in the terminal to stop the development server.

