# Conference Scraper

A Django web scraper that extracts conference session and poster data from the SGO 2026 meeting site and stores it in SQLite. It includes a dashboard, record browsing, search/filter, and CSV/XLSX export.

## ��� What it does

- Scrapes session data via `requests` + `BeautifulSoup`.
- Scrapes poster details via Selenium Chrome driver + detail page requests.
- Persists to `scraper.models.ConferenceItem`.
- UI and export endpoints:
  - `/` home
  - `/dashboard/` summary counts
  - `/records/` filter/paginate
  - `/export/csv/` and `/export/excel/`
  - `/admin/`

## ��� Code layout

- `conference_project/` (Django project)
  - `settings.py`, `urls.py`, etc.
- `scraper/` (Django app)
  - `models.py` (`ConferenceItem`)
  - `scraper.py` (scrape logic: `scrape_sessions`, `scrape_posters`, `run_all_scrapers`)
  - `management/commands/run_scraper.py`
  - `views.py`, `urls.py`, templates
- `setup_run.bat` (Windows bootstrap)
- `db.sqlite3` (local DB; should be ignored)

## ��� Requirements

- Python 3.11+
- Django==5.0.3
- requests
- beautifulsoup4
- pandas
- openpyxl
- lxml
- selenium
- webdriver-manager

## ⚙️ Setup (recommended)

The easiest way is the included batch bootstrap command (from repo root):

```powershell
./Conference-data-scraper/setup_run.bat
```

`setup_run.bat` does:
- Creates + activates virtual environment.
- Installs dependencies.
- Applies migrations.
- Creates default `admin/admin` superuser if missing.
- Starts server.

**Notably**: scraper execution is commented out to avoid automatic runs.

If you want manual setup instead:

```bash
python -m venv venv
# Windows cmd
venv\Scripts\activate
# Windows PowerShell
venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cd conference_project
python manage.py migrate
```

Optional:
```bash
python manage.py createsuperuser
```

## ▶️ Run scraper

From `conference_project/` run:
```bash
python manage.py run_scraper
```

This executes `run_all_scrapers()` that calls:
- `scrape_sessions()`
- `scrape_posters()`

## ▶️ Start web service

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## ��� Main app routes

- `/` home
- `/dashboard/` session/poster counts
- `/records/` list/search/paginate
- `/export/csv/` CSV download
- `/export/excel/` XLSX download
- `/admin/` Django admin

## ℹ️ Data model (`ConferenceItem`)

Includes fields like:
- `session_title`, `session_type`, `poster_title`
- `authors`, `affiliations`
- `date`, `time`, `location`, `session_category`, `presentation_type`
- `description`, `created_at`

## ���️ Summary of scraper logic

- `scrape_sessions()`:
  - fetch agenda page
  - parse `ul#agenda li`
  - fetch detail pages for date/time/location/category
  - dedupe by `session_title`, `date`, `time`

- `scrape_posters()`:
  - launch Chrome webdriver
  - parse `li.poster50x100` list
  - fetch each poster detail page
  - build record fields
  - dedupe by `poster_title`, `date`, `time`

## ��� Testing / verification

- `python manage.py run_scraper` should complete with logs and saved rows.
- Browse `/dashboard/` for counts.
- Browse `/records/`, filter/search/pagination.
- `/export/csv/` and `/export/excel/` return files.

## ��� Git cleanliness (recommended)

Add to `.gitignore`:
```
__pycache__/
*.pyc
db.sqlite3
```
Then remove tracked artifacts:
```bash
git rm --cached db.sqlite3
git rm -r --cached conference_project/**/__pycache__
```

## ��� Notes

- Selenium requires Chrome/Chromium + compatible driver (webdriver-manager handles auto-install usually).
- If poster scrape hangs or breaks, run session-only mode by temporarily changing `run_scraper` logic.
