@echo off
title SmartPrice India - Launcher
echo =====================================================================
echo              SMARTPRICE INDIA - SERVICE LAUNCHER
echo =====================================================================
echo.
echo Starting Backend API and Frontend React Client...
echo.

:: 1. Launch Backend Server in a new command prompt window (from the root folder)
echo [1/2] Starting FastAPI Server on port 8000...
start "SmartPrice Backend" cmd /k "echo Starting Backend Server... && .\backend\venv\Scripts\python.exe -m uvicorn backend.main:app --reload"

:: 2. Launch Frontend Server in another new command prompt window
echo [2/2] Starting React Dev Server on port 5173...
start "SmartPrice Frontend" cmd /k "echo Starting Frontend Client... && cd frontend && npm run dev"

echo.
echo =====================================================================
echo  Success! Both services are launching.
echo.
echo  - Backend API:   http://localhost:8000/docs (Swagger UI docs)
echo  - Frontend App:  http://localhost:5173
echo.
echo  (Keep the launched terminal windows open. Close them to stop services.)
echo =====================================================================
pause
