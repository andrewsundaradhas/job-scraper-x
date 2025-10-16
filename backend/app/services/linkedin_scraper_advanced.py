from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

try:
    from fake_useragent import UserAgent  # type: ignore
except Exception:  # pragma: no cover
    UserAgent = None  # Fallback handled below

from bs4 import BeautifulSoup  # type: ignore
import pandas as pd  # type: ignore


LINKEDIN_JOBS_SEARCH_URL = "https://www.linkedin.com/jobs/search/"


def _random_user_agent() -> str:
    if UserAgent is not None:
        try:
            return UserAgent().random
        except Exception:
            pass
    # Static fallback pool
    pool = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    ]
    return random.choice(pool)


def _sleep(min_s: float, max_s: float) -> None:
    time.sleep(random.uniform(min_s, max_s))


def _urlencode(params: Dict[str, Any]) -> str:
    from urllib.parse import urlencode

    return urlencode(params, doseq=True)


@dataclass
class ScrapeConfig:
    delay_min: float = 2.0
    delay_max: float = 5.0
    headless: bool = True
    use_proxy: bool = False
    proxy_url: Optional[str] = None
    max_pages: int = 10


class LinkedInJobScraper:
    def __init__(self, config: ScrapeConfig):
        self.config = config
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 15)

    def _setup_driver(self) -> webdriver.Chrome:
        options = ChromeOptions()
        if self.config.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Anti-detection flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f"user-agent={_random_user_agent()}")
        if self.config.use_proxy and self.config.proxy_url:
            options.add_argument(f"--proxy-server={self.config.proxy_url}")

        exe_path = ChromeDriverManager().install()
        service = ChromeService(executable_path=exe_path)
        driver = webdriver.Chrome(service=service, options=options)
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
        except Exception:
            pass
        driver.set_window_size(1920, 1080)
        return driver

    def _build_search_url(self, keywords: str, location: str, start: int = 0) -> str:
        params = {"keywords": keywords, "location": location}
        if start:
            params["start"] = start
        return f"{LINKEDIN_JOBS_SEARCH_URL}?{_urlencode(params)}"

    def _human_scroll(self, steps: int = 6) -> None:
        last = 0
        for _ in range(steps):
            self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight/6);")
            _sleep(self.config.delay_min / 3, self.config.delay_max / 2)
            new_h = self.driver.execute_script("return document.body.scrollHeight")
            if new_h == last:
                break
            last = new_h

    def _collect_cards_on_page(self) -> List[Dict[str, Any]]:
        jobs: List[Dict[str, Any]] = []
        cards = self.driver.find_elements(By.CSS_SELECTOR, "div.base-card")
        for card in cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title").text.strip()
            except NoSuchElementException:
                title = ""
            company = None
            try:
                company = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle").text.strip()
            except NoSuchElementException:
                pass
            location = None
            try:
                location = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location").text.strip()
            except NoSuchElementException:
                pass
            link = ""
            try:
                link = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link").get_attribute("href")
            except NoSuchElementException:
                pass
            posted = None
            try:
                t = card.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                posted = t.split("T")[0] if t else None
            except NoSuchElementException:
                pass

            if link:
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "job_link": link,
                    "posted_date": posted,
                })
        return jobs

    def _extract_details(self, job_url: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        try:
            self.driver.get(job_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            _sleep(self.config.delay_min, self.config.delay_max)
            self._human_scroll(steps=4)
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            desc = soup.select_one("div.description__text, div.show-more-less-html__markup")
            data["description_html"] = str(desc) if desc else None
            data["description_text"] = desc.get_text("\n").strip() if desc else None

            criteria = [li.get_text(" ", strip=True) for li in soup.select("li.description__job-criteria-item")]
            data["criteria"] = criteria

            # Best-effort extraction for structured fields
            text = data.get("description_text") or ""
            for key in ["Full-time", "Part-time", "Contract", "Internship", "Temporary"]:
                if key.lower() in text.lower():
                    data["employment_type"] = key
                    break
        except WebDriverException:
            pass
        return data

    def search_and_collect(self, keywords: str, location: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        start = 0
        for page in range(self.config.max_pages):
            url = self._build_search_url(keywords, location, start=start)
            self.driver.get(url)
            try:
                self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.base-card")))
            except TimeoutException:
                break

            self._human_scroll(steps=8)
            batch = self._collect_cards_on_page()
            if not batch:
                break
            results.extend(batch)

            start += 25  # LinkedIn paginates in ~25 increments
            _sleep(self.config.delay_min, self.config.delay_max)
        # Deduplicate by job_link
        seen = set()
        unique: List[Dict[str, Any]] = []
        for j in results:
            k = j.get("job_link")
            if k and k not in seen:
                unique.append(j)
                seen.add(k)
        return unique

    def enrich_details(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched: List[Dict[str, Any]] = []
        for j in jobs:
            details = self._extract_details(j["job_link"]) if j.get("job_link") else {}
            enriched.append({**j, **details})
            _sleep(self.config.delay_min, self.config.delay_max)
        return enriched

    @staticmethod
    def _ensure_dir(path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def export(self, records: List[Dict[str, Any]], out_dir: str, base_name: str) -> Dict[str, str]:
        self._ensure_dir(out_dir)
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        csv_path = os.path.join(out_dir, f"{base_name}-{ts}.csv")
        json_path = os.path.join(out_dir, f"{base_name}-{ts}.json")
        df = pd.DataFrame.from_records(records)
        df.to_csv(csv_path, index=False)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return {"csv": csv_path, "json": json_path}

    def close(self) -> None:
        try:
            self.driver.quit()
        except Exception:
            pass


def run_advanced_scrape(keywords: str, location: str, out_dir: str, config: Optional[ScrapeConfig] = None, enrich: bool = True) -> Dict[str, Any]:
    cfg = config or ScrapeConfig()
    scraper = LinkedInJobScraper(cfg)
    try:
        listings = scraper.search_and_collect(keywords, location)
        records = scraper.enrich_details(listings) if enrich else listings
        files = scraper.export(records, out_dir=out_dir, base_name=f"{keywords}-{location}".replace(" ", "_"))
        return {
            "found": len(listings),
            "exported": len(records),
            "files": files,
        }
    finally:
        scraper.close()


