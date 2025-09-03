import os
import pytz
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ipo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== API CONFIGURATION =====
API_KEY = os.getenv("BREVO_API_KEY")
FROM_NAME = os.getenv("FROM_NAME")
FROM_EMAIL = os.getenv("FROM_EMAIL")
ADMIN_EMAIL = os.getenv("TO_EMAIL")
ONGOING_URL = os.getenv("ONGOING_URL")

# ===== BOT CONFIGURATION =====
TOTAL_APPS = int(os.getenv("TOTAL_APPS", 2500000))
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", 5))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # <-- directory of config.py
EMAIL_LIST_FILE = os.path.join(BASE_DIR, "email_update.txt")

# ===== DISCORD CONFIGURATION =====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = 1411629709220909078
DISCORD_CHANNEL_ID = 1412333785776656464

# ===== TIMEZONE =====
NEPAL_TZ = pytz.timezone('Asia/Kathmandu')

# ===== VALIDATION =====
def validate_environment():
    """Validate required environment variables"""
    required_vars = ["BREVO_API_KEY", "FROM_NAME", "FROM_EMAIL", "TO_EMAIL", "ONGOING_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file")
        return False
    return True