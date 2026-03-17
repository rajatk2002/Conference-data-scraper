from django.core.management.base import BaseCommand
from scraper.scraper import run_all_scrapers, scrape_posters, scrape_sessions


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        run_all_scrapers()

        # scrape_posters()
        
        # scrape_sessions()

        self.stdout.write("Scraping completed!")