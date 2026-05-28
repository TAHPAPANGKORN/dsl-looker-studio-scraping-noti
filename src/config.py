from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from environment variables and defaults."""
    
    # File Paths
    workspace_dir: Path = Path(__file__).resolve().parent.parent
    users_file: Path = workspace_dir / "users.json"
    state_file: Path = workspace_dir / "state.json"
    
    # SMTP Server Settings
    smtp_server: str = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.environ.get("SMTP_PORT", "587"))
    
    # Sender Credentials
    sender_email: Optional[str] = os.environ.get("SENDER_EMAIL")
    sender_password: Optional[str] = os.environ.get("SENDER_PASSWORD")
    
    # Google Sheet URL (alternative source for user lists)
    google_sheet_csv_url: Optional[str] = os.environ.get("GOOGLE_SHEET_CSV_URL")
    
    # GitHub Action Config Secret (JSON string containing array of users)
    users_config_json: Optional[str] = os.environ.get("USERS_CONFIG")
    
    def __post_init__(self) -> None:
        # Strip and clean sender credentials
        if self.sender_email:
            object.__setattr__(self, "sender_email", self.sender_email.strip())
        if self.sender_password:
            cleaned_pwd = self.sender_password.strip().replace(" ", "")
            object.__setattr__(self, "sender_password", cleaned_pwd)
