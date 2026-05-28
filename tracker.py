import argparse
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file before imports that use them
load_dotenv()

from src.config import AppConfig
from src.user_loader import UserLoader
from src.state import StateManager
from src.scraper import LookerScraper
from src.notifier import EmailNotifier

# Setup professional logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("looker_tracker")

def run_pipeline(args: argparse.Namespace) -> None:
    """Executes the tracking pipeline, checking status updates and notifying users."""
    logger.info("Initializing Looker Studio Tracker Application")
    config = AppConfig()
    
    # Load users
    loader = UserLoader(config)
    users = loader.load_users()
    if not users:
        logger.error("No target users configured. Check users.json or environment secrets.")
        return
        
    logger.info(f"Loaded {len(users)} users to process.")
    
    # Initialize managers
    state_manager = StateManager(config.state_file)
    state = state_manager.load_state()
    state_changed = False
    
    notifier = EmailNotifier(config)
    
    # Use context manager to reuse a single browser instance across all users
    with LookerScraper(headless=not args.headful) as scraper:
        for user in users:
            user_id = user.get("id")
            name = user.get("name")
            email = user.get("email")
            url = user.get("url")
            student_id = user.get("student_id")
            
            logger.info(f"Processing student: {name} (Student ID: {student_id})")
            
            try:
                # Scrape Looker Studio dashboard
                current_status = scraper.scrape(url, student_id)
                if not current_status:
                    logger.warning(f"No status data extracted for student: {name}")
                    continue
                    
                # Retrieve cached status
                user_state = state.get(user_id, {})
                last_known_status = user_state.get("last_known_status")
                
                # Check for changes in tracked fields
                if state_manager.has_changes(last_known_status, current_status):
                    logger.info(f"Status update detected for {name}. Dispatching email notification...")
                    
                    # Send email notification
                    email_sent = notifier.send_notification(
                        receiver_email=email,
                        name=name,
                        new_status=current_status,
                        dashboard_url=url
                    )
                    
                    if email_sent:
                        # Update local state cache
                        state[user_id] = {
                            "last_known_status": current_status,
                            "last_checked": datetime.now().isoformat()
                        }
                        state_changed = True
                else:
                    logger.info(f"No updates detected for {name}. Current status matches cache.")
                    # Update last checked timestamp
                    if user_id in state:
                        state[user_id]["last_checked"] = datetime.now().isoformat()
                        state_changed = True
                        
            except Exception as e:
                logger.error(f"Error checking tracking status for student {name}: {e}", exc_info=True)
            
    # Save updated state
    if state_changed:
        state_manager.save_state(state)
    else:
        logger.info("No state modifications written.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Looker Studio กยศ. Tracker Pipeline")
    parser.add_argument("--headful", action="store_true", help="Launch browser in visible (headful) mode")
    args = parser.parse_args()
    
    logger.info("--- Starting Tracker Execution ---")
    run_pipeline(args)
    logger.info("--- Tracker Execution Completed ---")

if __name__ == "__main__":
    main()
