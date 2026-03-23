@echo off
TITLE RepoSage runner
echo =======================================================
echo               Starting RepoSage
echo =======================================================

echo [1/2] Launching FastAPI Backend in a separate window...
start "RepoSage FastAPI Backend" cmd /c "conda run -n reposage uvicorn main:app --host 0.0.0.0 --port 8000"

echo Wait for backend to warm up (5 seconds)...
timeout /t 5 /nobreak > nul

echo [2/2] Launching Streamlit UI...
conda run -n reposage streamlit run app.py

echo =======================================================
echo RepoSage is running!
echo Backend: http://localhost:8000
echo Frontend: Usually http://localhost:8501
echo =======================================================

pause
