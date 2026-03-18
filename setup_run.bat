@echo off
setlocal enabledelayedexpansion

REM ------------------------------------------------------------------
REM Conference Scraper Bootstrap Script (Windows)
REM Usage: clone repo, open cmd in repo root, run setup_run.bat
REM ------------------------------------------------------------------

echo ========================
echo Conference Scraper Setup
echo ========================

echo [1/8] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not on PATH.
    echo Install Python 3.11+ and rerun.
    pause
    exit /b 1
)

echo [2/8] Create virtual environment if not exists...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo venv already exists.
)

echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
if "%VIRTUAL_ENV%"=="" (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [4/8] Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b 1
)

cd conference_project

echo [5/8] Applying Django migrations...
python manage.py migrate --noinput
if errorlevel 1 (
    echo ERROR: Migrations failed.
    pause
    exit /b 1
)

echo [6/8] Ensuring superuser admin/admin exists...
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); u='admin'; pw='admin'; e='admin@example.com';
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=pw); print('Created superuser admin')
else:
    print('Superuser admin already exists')"
if errorlevel 1 (
    echo WARNING: Failed to create/verify superuser.
)

echo [7/8] Running data scraper (sessions + posters)...
python manage.py run_scraper
if errorlevel 1 (
    echo ERROR: Scraper command failed.
    pause
    exit /b 1
)

echo [8/8] Starting Django development server on http://127.0.0.1:8000
python manage.py runserver

endlocal
