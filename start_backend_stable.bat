@echo off
cd backend
python -m uvicorn main:app --port 8000
pause
