from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from ..config import settings


LINKEDIN_JOBS_SEARCH_URL = "https://www.linkedin.com/jobs/search/"

# CSS selectors based on the provided config
SELECTORS = {
	"job_cards": "div.base-card",
	"title": "h3.base-search-card__title",
	"company": "h4.base-search-card__subtitle",
	"location": "span.job-search-card__location",
	"posted_date": "time",
	"job_link": "a.base-card__full-link",
}


def _build_search_url(keywords: str, location: str) -> str:
	# Basic query params; more filters can be appended (experience, type)
	from urllib.parse import urlencode

	params = {
		"keywords": keywords,
		"location": location,
	}
	return f"{LINKEDIN_JOBS_SEARCH_URL}?{urlencode(params)}"


def _init_driver() -> webdriver.Chrome:
	options = Options()
	if settings.selenium_headless:
		options.add_argument("--headless=new")
	options.add_argument("--disable-gpu")
	options.add_argument("--no-sandbox")
	options.add_argument("--window-size=1920,1080")
	# Choose driver path: configured path or manager-installed
	if settings.chrome_driver_path:
		service = ChromeService(executable_path=settings.chrome_driver_path)
	else:
		exe_path = ChromeDriverManager().install()
		service = ChromeService(executable_path=exe_path)
	return webdriver.Chrome(service=service, options=options)


def scrape_linkedin_jobs(keywords: str, location: str, max_pages: int = 10) -> List[dict]:
	url = _build_search_url(keywords, location)
	driver = _init_driver()
	jobs: List[dict] = []
	try:
		driver.get(url)
		wait = WebDriverWait(driver, 15)
		current_page = 1
        while current_page <= max_pages:
			try:
				wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELECTORS["job_cards"])) )
			except TimeoutException:
				break

            # Try to load more cards by scrolling
            last_height = 0
            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(driver, 5).until(lambda d: True)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            cards = driver.find_elements(By.CSS_SELECTOR, SELECTORS["job_cards"]) or []
			for card in cards:
				try:
					title_el = card.find_element(By.CSS_SELECTOR, SELECTORS["title"]) if SELECTORS["title"] else None
					company_el = card.find_element(By.CSS_SELECTOR, SELECTORS["company"]) if SELECTORS["company"] else None
					location_el = card.find_element(By.CSS_SELECTOR, SELECTORS["location"]) if SELECTORS["location"] else None
					posted_el = card.find_element(By.CSS_SELECTOR, SELECTORS["posted_date"]) if SELECTORS["posted_date"] else None
					link_el = card.find_element(By.CSS_SELECTOR, SELECTORS["job_link"]) if SELECTORS["job_link"] else None

					job = {
						"title": (title_el.text or "").strip() if title_el else "",
						"company": (company_el.text or "").strip() if company_el else None,
						"location": (location_el.text or "").strip() if location_el else None,
						"posted_date": None,
						"job_link": link_el.get_attribute("href") if link_el else "",
						"experience_level": None,
						"job_type": None,
						"keywords": keywords,
					}

					if posted_el and posted_el.get_attribute("datetime"):
						# LinkedIn time tag often includes datetime attribute
						job["posted_date"] = posted_el.get_attribute("datetime").split("T")[0]

					jobs.append(job)
				except NoSuchElementException:
					continue

			# Pagination: look for a next button
            next_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Next'], button[aria-label='Next page']")
			if next_buttons:
				next_btn = next_buttons[0]
				if next_btn.is_enabled():
                    next_btn.click()
                    # small delay to mimic human behavior and avoid rate limiting
                    driver.implicitly_wait(1)
					current_page += 1
					continue
			break
	finally:
		driver.quit()
	return jobs

