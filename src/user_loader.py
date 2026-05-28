import csv
import json
import logging
import urllib.request
from typing import Any, Dict, List
from src.config import AppConfig

logger = logging.getLogger(__name__)

class UserLoader:
    """Resolves and loads the list of monitored users from config, JSON files, or CSV endpoints."""
    
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def load_users(self) -> List[Dict[str, Any]]:
        """Resolves target users using configurations by priority order."""
        # 1. Google Sheets CSV endpoint
        if self.config.google_sheet_csv_url:
            users = self._fetch_csv_users(self.config.google_sheet_csv_url)
            if users:
                return users
                
        # 2. Config JSON String (secrets environment configuration)
        if self.config.users_config_json:
            try:
                users = json.loads(self.config.users_config_json)
                if isinstance(users, list):
                    return users
            except Exception as e:
                logger.error(f"Failed to parse USERS_CONFIG JSON environment variable: {e}")
                
        # 3. Fallback to local users.json file
        if self.config.users_file.exists():
            try:
                with open(self.config.users_file, "r", encoding="utf-8") as f:
                    users = json.load(f)
                    if isinstance(users, list):
                        return users
            except Exception as e:
                logger.error(f"Failed to read local users file {self.config.users_file}: {e}")
                
        return []

    def _fetch_csv_users(self, csv_url: str) -> List[Dict[str, Any]]:
        """Fetches and parses users registered via remote Google Sheets CSV endpoint."""
        logger.info(f"Fetching user registrations from Google Sheet endpoint...")
        users: List[Dict[str, Any]] = []
        try:
            req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                csv_data = response.read().decode('utf-8').splitlines()
            
            reader = csv.DictReader(csv_data)
            for idx, row in enumerate(reader):
                # Normalization helper for flexible column names in Thai and English
                def get_val(row_dict: Dict[str, str], keys: List[str]) -> str:
                    for k, val in row_dict.items():
                        if any(key.lower() in k.lower() for key in keys):
                            return val.strip()
                    return ""

                name = get_val(row, ["ชื่อ", "name"])
                email = get_val(row, ["อีเมล", "email", "mail"])
                url = get_val(row, ["looker", "url", "ลิงก์", "link"])
                student_id = get_val(row, ["รหัส", "student_id", "student id"])
                
                if not email or not url:
                    logger.warning(f"Row {idx + 1} skipped due to missing email or Looker Studio URL.")
                    continue
                    
                user_id = student_id if student_id else f"user_{idx + 1}"
                users.append({
                    "id": user_id,
                    "name": name if name else f"User {idx + 1}",
                    "email": email,
                    "url": url,
                    "student_id": student_id
                })
            logger.info(f"Retrieved {len(users)} users from CSV endpoint.")
            return users
        except Exception as e:
            logger.error(f"Failed to fetch CSV registrations from Sheets: {e}")
            return []
