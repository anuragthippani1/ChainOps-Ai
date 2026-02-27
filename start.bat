@echo off
echo Starting ChainOps AI - Multi-Agent Supply Chain Risk Intelligence Platform
echo.

echo Installing dependencies...
call npm run install-all

echo.
echo Starting ChainOps AI...
echo Backend will run on http://localhost:8000
echo Frontend will run on http://localhost:3000
echo.

call npm run dev

pause
