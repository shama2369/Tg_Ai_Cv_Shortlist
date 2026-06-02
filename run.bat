@echo off
REM Activate virtual environment and run FastAPI app
echo ========================================
echo AI CV Shortlisting API
echo ========================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Verifying Python environment...
venv\Scripts\python.exe -c "import sys; print('Python:', sys.executable); print('Version:', sys.version)"
echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause

