@echo off
setlocal

cd /d "%~dp0\.."

where python >nul 2>nul
if errorlevel 1 (
  echo python is required but was not found.
  exit /b 1
)

if not exist ".venv" (
  python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt

if "%TREND_TO_COMMERCE_DATA_DIR%"=="" set "TREND_TO_COMMERCE_DATA_DIR=%cd%\Data"
if "%TREND_TO_COMMERCE_DB_PATH%"=="" set "TREND_TO_COMMERCE_DB_PATH=%cd%\backend\trend_to_commerce.db"
if "%TREND_TO_COMMERCE_LOAD_RTF_ENV%"=="" set "TREND_TO_COMMERCE_LOAD_RTF_ENV=1"
if "%GENERATION_PREFER_REMOTE%"=="" set "GENERATION_PREFER_REMOTE=1"
if "%TREND_TO_COMMERCE_PORT%"=="" set "TREND_TO_COMMERCE_PORT=8000"

echo Starting Trend-to-Commerce at http://127.0.0.1:%TREND_TO_COMMERCE_PORT%
uvicorn backend.app.main:app --host 127.0.0.1 --port %TREND_TO_COMMERCE_PORT%
