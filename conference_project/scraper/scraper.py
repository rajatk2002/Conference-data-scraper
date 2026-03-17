import requests
from bs4 import BeautifulSoup
from scraper.models import ConferenceItem

from urllib.parse import urljoin
import time
import pandas as pd

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_SITE = "https://sgo2026annualmeeting.eventscribe.net/"

SESSION_URL = BASE_SITE + "SearchByPresentation.asp?pfp=Browse%20by%20Title"

POSTER_URL = BASE_SITE + "posters/browseByPosterTitle.asp?pfp=BrowsebyTitle"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_session_details(detail_url):
    try:
        response = requests.get(detail_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        date = "N/A"
        date_icon = soup.select_one(".fa-calendar")

        if date_icon:
            parent_div = date_icon.parent
            if parent_div:
                texts = [t.strip() for t in parent_div.contents if isinstance(t, str) and t.strip()]
                if texts:
                    date = texts[0]

        time_range = "N/A"
        time_icon = soup.select_one(".fa-clock-o")

        if time_icon:
            time_span = time_icon.find_next("span")
            if time_span:
                time_range = time_span.get_text(strip=True)
                if "AST" not in time_range:
                    time_range = time_range + " AST"

        location = "N/A"
        location_icon = soup.select_one(".fa-map-marker")
        if location_icon:
            location = location_icon.find_next("span").get_text(strip=True)
            location = location.replace("Location:", "").strip()

        category = "N/A"
        category_tag = soup.select_one(".trackname span")
        if category_tag:
            category = category_tag.get_text(strip=True)

        return date, time_range, location, category

    except Exception as e:
        print(f"Error fetching detail page: {e}")
        return "N/A", "N/A", "N/A", "N/A"


def scrape_sessions():
    response = requests.get(SESSION_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    agenda = soup.select_one("ul#agenda")
    items = agenda.find_all("li") if agenda else []
    print(f"Total items detected: {len(items)}")

    current_day = "N/A"
    count = 0

    for item in items:

        if not item.get_text(strip=True):
            continue

        if "dayrow" in item.get("class", []):
            current_day = item.get_text(strip=True)
            continue

        title_tag = item.select_one(".prestitle span")
        session_title = title_tag.get_text(strip=True) if title_tag else "N/A"

        hidden_tag = item.select_one("i.hidden")
        authors = []
        affiliations = []
        presentation_type = "N/A"

        if hidden_tag:
            hidden_text = hidden_tag.get_text(strip=True)
            parts = hidden_text.split("###")

            if parts:
                if "–" in parts[0]:
                    author_part, affiliation_part = parts[0].split("–", 1)
                    authors = [a.strip() for a in author_part.split(",")]
                    affiliations = [affiliation_part.strip()]

                if len(parts) > 2:
                    presentation_type = parts[2].strip()

        session_type = "Session"

        data_url = item.get("data-url")
        detail_url = urljoin(BASE_SITE, data_url) if data_url else None

        if detail_url:
            date, time_range, location, category = get_session_details(detail_url)
        else:
            date, time_range, location, category = current_day, "N/A", "N/A", "N/A"

        existing = ConferenceItem.objects.filter(
            session_title=session_title,
            date=date,
            time=time_range
        ).first()

        if existing:
            conference_item = existing
            created = False
        else:
            conference_item = ConferenceItem.objects.create(
                session_title=session_title,
                session_type=session_type,
                authors=", ".join(authors),
                affiliations=", ".join(affiliations),
                date=date,
                time=time_range,
                location=location,
                session_category=category,
                presentation_type=presentation_type,
            )
            created = True

        if created:
            count += 1
            print(f"[{count}] Saved: {conference_item.session_title}")

    print(f"Total saved items: {count}")



def scrape_posters():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.get(POSTER_URL)

    posters = driver.find_elements(By.CSS_SELECTOR, "li.poster50x100")
    print("Total posters found:", len(posters))

    count = 0

    for poster in posters:
        try:
            poster_number = poster.find_element(By.CSS_SELECTOR, ".prestime span").text
            title = poster.find_element(By.CSS_SELECTOR, ".prestitle span").text

            data_url = poster.get_attribute("data-url")
            detail_url = urljoin(BASE_SITE, data_url)

            resp = requests.get(detail_url)
            soup = BeautifulSoup(resp.text, "lxml")
            content = soup.select_one(".popup_content")

            title = "NA"
            h1_tag = content.select_one("h1")
            if h1_tag:
                title = h1_tag.get_text(strip=True)

            category = "NA"
            category_tag = content.select_one(".trackname span")
            if category_tag:
                category = category_tag.get_text(strip=True)

            date = "NA"
            date_icon = content.select_one(".fa-calendar")
            if date_icon:
                date = date_icon.parent.get_text(strip=True)

            time_text = "NA"
            time_icon = content.select_one(".fa-clock-o")
            if time_icon:
                span = time_icon.find_next("span")
                if span:
                    time_text = span.get_text(" ", strip=True)
                    time_text = time_text.replace("\n", " ").strip()

                    if not time_text.endswith("AST"):
                        time_text += " AST"

            location = "NA"

            location_icon = content.select_one(".fa-map-marker")

            if location_icon:
                parent_div = location_icon.find_parent("div")
                if parent_div:
                    text = parent_div.get_text(" ", strip=True)
                    location = text.replace("Location:", "").strip()

            authors_tags = content.select(".speaker-name")
            authors = ", ".join([a.get_text(strip=True) for a in authors_tags]) if authors_tags else "NA"

            aff_tags = content.select(".prof-text")
            affiliations = "; ".join([
                " ".join(a.stripped_strings) for a in aff_tags
            ]) if aff_tags else "NA"

            description = "NA"
            desc_tag = content.select_one(".abstracttext")
            if desc_tag:
                description = desc_tag.get_text(strip=True)

            existing = ConferenceItem.objects.filter(
                poster_title=title,
                date=date,
                time=time_text
            ).first()

            if existing:
                conference_item = existing
                created = False
            else:
                conference_item = ConferenceItem.objects.create(
                    session_type="Poster",
                    poster_title=title,
                    authors=authors,
                    affiliations=affiliations,
                    date=date,
                    time=time_text,
                    location=location,
                    session_category=None,
                    presentation_type=None,
                    description=description
                )
                created = True

            if created:
                count += 1
                print(f"[{count}] Saved: {conference_item.poster_title}")

        except Exception as e:
            print(f"Error processing poster: {e}")
            continue

    print(f"Total new posters saved: {count}")

    driver.quit()


def run_all_scrapers():

    try:
        scrape_sessions()

        scrape_posters()
    except Exception as e:
        print(f"Error during scraping: {e}")