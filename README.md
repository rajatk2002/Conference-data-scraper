# Conference Scraper

A Django-based web project that scrapes conference session and poster data (SGO 2026 meeting) and stores it in a SQLite database. It provides a simple dashboard and record browsing UI, with CSV/Excel export support.

## Project structure

- `conference_project/` – Django project folder
  - `conference_project/settings.py` – Django settings
  - `conference_project/urls.py` – root URL config
  - `wsgi.py`, etc.
- `scraper/` – main Django app
  - `models.py` – `ConferenceItem` model
  - `scraper.py` – scraping routines (sessions + posters)
  - `management/commands/run_scraper.py` – CLI command to run all scrapers
  - `views.py` – dashboard, records + export views
  - `urls.py` – app routes
  - `templates/` – HTML templates for home/dashboard/records
- `db.sqlite3` – SQLite DB created at runtime
- `requirements.txt` – Python dependencies

## Dependencies

```
Django==5.0.3
requests==2.31.0
beautifulsoup4==4.12.3
pandas==2.2.1
openpyxl==3.1.2
lxml==6.0.2
selenium==4.41.0
webdriver-manager==4.0.1
```

## Quick setup

1. Clone / copy repository
2. Create and activate virtual environment

```bash
python -m venv venv
# Windows (cmd):
venv\Scripts\activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Unix:
source venv/bin/activate
```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. Apply migrations

```bash
cd conference_project
python manage.py migrate
```

5. (Optional) Create superuser for Django admin

```bash
python manage.py createsuperuser
```

## Chrome WebDriver note

The poster scraper uses `selenium.webdriver.Chrome`.
- Install Chrome browser (or use Chromium).
- `webdriver-manager` should auto-download proper driver with current dependencies.
- If driver issues appear, install/upgrade manually or use environment settings.

## Run scraper

From `conference_project/` run:

```bash
python manage.py run_scraper
```

This executes `run_all_scrapers()` in `scraper/scraper.py`:
- `scrape_sessions()` (requests + BeautifulSoup)
- `scrape_posters()` (Selenium + requests + BeautifulSoup)

All results are saved to `scraper.ConferenceItem` in `db.sqlite3`.

## Run web server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Routes:
- `/` – Home page
- `/dashboard/` – counts of sessions/posters/authors
- `/records/` – searchable/paginated list of records
- `/export/csv/` – CSV export of conference data
- `/export/excel/` – XLSX export of conference data
- `/admin/` – Django admin (if superuser configured)

## Usage

1. Run scraper first (`python manage.py run_scraper`).
2. Start server (`python manage.py runserver`).
3. Navigate to dashboard to confirm row counts.
4. Use records for filtering and exports.
5. In records page, set search terms, session/poster filter, page size and pagination.

## Data model (`ConferenceItem`)

Fields:
- `session_title` (text)
- `session_type` (`Session`/`Poster`)
- `poster_title`, `authors`, `affiliations`
- `date`, `time`, `location`, `session_category`, `presentation_type`, `description`
- `created_at` timestamp

## Testing

No dedicated tests defined yet. Quick manual tests:
1. `python manage.py run_scraper` success output
2. Browse `/dashboard/` returns counts
3. `/records/?search=WXYZ` works
4. Export endpoints download files

## Troubleshooting

- If `selenium` fails: verify Chrome version + matching driver.
- If no records appear: re-run scraper, check console logs for errors.
- If `module not found`: double-check virtualenv and `pip install -r requirements.txt`.

## Contribution

- Add more field extraction in `scraper/scraper.py`.
- Add robust error handling and retry logic for network failures.
- Create unit tests under `scraper/tests.py`.
- Add CI lint/test scripts.
