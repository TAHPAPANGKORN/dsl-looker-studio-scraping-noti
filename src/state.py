from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from src.models import CLASS_FIELD_MAP

logger = logging.getLogger(__name__)

class StateManager:
    """Manages local state loading, saving, and change detection."""
    
    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file
        
    def load_state(self) -> Dict[str, Any]:
        """Loads cached state from JSON file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
            except Exception as e:
                logger.error(f"Failed to load state file: {e}")
        return {}
        
    def save_state(self, state: Dict[str, Any]) -> None:
        """Saves current state to JSON file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info("Saved state to file.")
        except Exception as e:
            logger.error(f"Failed to save state file: {e}")

    @staticmethod
    def normalize_value(v: Any) -> str:
        """Normalizes status values to strip whitespace and treat equivalent empty values equally."""
        if v is None:
            return ""
        v_str = str(v).strip()
        if v_str in ["", "-", "ไม่มีข้อมูล"]:
            return ""
        return v_str

    def has_changes(self, old_status: Optional[Dict[str, Any]], new_status: Dict[str, Any]) -> bool:
        """Detects if any of the coordinate-mapped fields have changed compared to the cached state."""
        if not old_status or not isinstance(old_status, dict):
            return True
            
        for k in CLASS_FIELD_MAP.values():
            old_val = self.normalize_value(old_status.get(k))
            new_val = self.normalize_value(new_status.get(k))
            if old_val != new_val:
                logger.debug(f"Field '{k}' changed from '{old_val}' to '{new_val}'")
                return True
        return False
