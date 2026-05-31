from datetime import datetime
import logging
import re
import time
from typing import Any, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser, Playwright
from src.models import CLASS_FIELD_MAP

logger = logging.getLogger(__name__)

class LookerScraper:
    """Scrapes student checklist details from a Google Looker Studio dashboard.
    
    Supports context manager protocol to reuse the same browser instance across runs.
    """
    
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

    def __enter__(self) -> "LookerScraper":
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=self.headless)
        logger.info("Browser instance launched successfully.")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.browser:
            self.browser.close()
            logger.info("Browser instance closed.")
        if self._playwright:
            self._playwright.stop()

    def scrape(self, url: str, student_id: str) -> Optional[Dict[str, Any]]:
        """Navigates to Looker Studio URL in a new context, filters, and extracts status values.
        Supports up to 2 retries if rendering errors are detected.
        """
        if not self.browser:
            raise RuntimeError("Scraper must be used as a context manager (with LookerScraper() as scraper).")
            
        logger.info(f"Scraping student details for: {student_id} from {url}")
        
        # Create an isolated page context for this request
        context = self.browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page: Page = context.new_page()
        
        try:
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.warning(f"Retrying scraping for student {student_id} (Attempt {attempt}/{max_retries})...")
                        # Reload page
                        page.reload(wait_until="load")
                    else:
                        page.goto(url, wait_until="load")
                    
                    logger.info("Waiting for dashboard component assets to mount (15s)...")
                    time.sleep(15)
                    
                    if student_id:
                        self._apply_student_filter(page, student_id)
                        
                    data = self._extract_table_data(page)
                    
                    # Check for rendering errors in data
                    if self._has_rendering_errors(data):
                        logger.warning(f"Looker Studio rendering errors detected in extracted data on attempt {attempt}.")
                        if attempt < max_retries:
                            continue
                        else:
                            logger.error(f"Failed to scrape student {student_id} after {max_retries} retries due to persistent rendering errors.")
                            return None
                    
                    return data
                except Exception as e:
                    logger.error(f"Error during scrape attempt {attempt} for student {student_id}: {e}", exc_info=True)
                    if attempt >= max_retries:
                        return None
        finally:
            context.close()

    def _apply_student_filter(self, page: Page, student_id: str) -> None:
        """Finds the text input filter box, types the student ID, and presses Enter."""
        logger.info(f"Filtering dashboard results for Student ID: {student_id}")
        inputs = page.locator('input[type="text"]')
        
        if inputs.count() > 0:
            target_input = inputs.first
            try:
                target_input.click()
                # Clear and fill the input reliably
                target_input.fill(student_id)
                time.sleep(1)
                target_input.press("Enter")
                logger.info("Student ID filter applied. Waiting for data refresh (12s)...")
                time.sleep(12)
            except Exception as e:
                logger.warning(f"Failed to enter student ID in looker text input: {e}")
        else:
            logger.warning("No editable text input fields detected on dashboard canvas.")

    def _extract_table_data(self, page: Page) -> Dict[str, str]:
        """Extracts text contents from scorecards/simple-table components matching CLASS_FIELD_MAP."""
        logger.info("Extracting data cards...")
        extracted_data: Dict[str, str] = {}
        
        tables = page.locator(".lego-component.simple-table").all()
        logger.info(f"Found {len(tables)} tables to inspect.")
        
        for table in tables:
            try:
                cls = table.get_attribute("class") or ""
                cd_class_list = [c for c in cls.split() if c.startswith("cd-")]
                if not cd_class_list:
                    continue
                cd_name = cd_class_list[0]
                
                if cd_name in CLASS_FIELD_MAP:
                    field_name = CLASS_FIELD_MAP[cd_name]
                    text_content = table.text_content() or ""
                    normalized_text = re.sub(r'\s+', ' ', text_content).strip()
                    cleaned_value = normalized_text.replace("ไม่มีข้อมูล", "").replace("No data-", "").replace("No data", "").strip()
                    extracted_data[field_name] = cleaned_value
            except Exception as e:
                logger.error(f"Error reading simple-table cell elements: {e}")
                
        return extracted_data

    def _has_rendering_errors(self, data: Dict[str, str]) -> bool:
        """Checks if any extracted value contains Looker Studio rendering error keywords."""
        error_keywords = [
            "invalid dimension",
            "this chart has an invalid dimension",
            "see details",
            "system error",
            "encountered a system error",
            "the server encountered an error"
        ]
        if not data:
            return False
            
        for key, value in data.items():
            val_lower = str(value).lower()
            for keyword in error_keywords:
                if keyword in val_lower:
                    logger.warning(f"Found error keyword '{keyword}' in field '{key}': '{value}'")
                    return True
        return False

