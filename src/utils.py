import os
from datetime import datetime
from config import NEPAL_TZ, EMAIL_LIST_FILE, logger


def get_nepal_time():
    """Get current time in Nepal timezone"""
    return datetime.now(NEPAL_TZ)


def get_nepal_date_str():
    """Get current date string in Nepal timezone (YYYY-MM-DD format)"""
    return get_nepal_time().strftime("%Y-%m-%d")


def load_email_list():
    """Load email addresses from email_update.txt file"""
    try:
        if not os.path.exists(EMAIL_LIST_FILE):
            logger.warning(f"{EMAIL_LIST_FILE} not found. Creating empty file.")
            with open(EMAIL_LIST_FILE, 'w') as f:
                f.write("# Add email addresses (one per line)\n")
                f.write("# Lines starting with # are comments\n")
            return []
        
        emails = []
        with open(EMAIL_LIST_FILE, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Basic email validation
                if '@' in line and '.' in line.split('@')[-1]:
                    emails.append(line.lower())
                else:
                    logger.warning(f"Invalid email format on line {line_num}: {line}")
        
        logger.info(f"Loaded {len(emails)} email addresses from {EMAIL_LIST_FILE}")
        return emails
    
    except Exception as e:
        logger.error(f"Error loading email list: {e}")
        return []


def calculate_ipo_metrics(ipo, current_date_str):
    """Calculate IPO metrics like probability and suggestions"""
    try:
        close_date = ipo.get("close_date", "").split(" ")[0] if ipo.get("close_date") else None
        if not close_date:
            return 0, "10", "Unable to calculate metrics - missing close date"
        
        # Calculate remaining days
        close_datetime = datetime.strptime(close_date, "%Y-%m-%d")
        current_datetime = datetime.strptime(current_date_str, "%Y-%m-%d")
        rem_days = (close_datetime - current_datetime).days
        
        # Calculate probability and suggestions
        from config import TOTAL_APPS
        shares_offered = ipo.get('shares_offered', 0)
        prob = (shares_offered / TOTAL_APPS) * 100 if shares_offered > 0 else 0
        
        sug_qty = "10" if prob < 90 else "more than 10"
        suggestion = (
            "Conservative approach recommended due to high demand."
            if prob < 90
            else "Higher allocation possible due to favorable probability."
        )
        
        return rem_days, prob, sug_qty, suggestion
        
    except ValueError as e:
        logger.error(f"Date parsing error for {ipo.get('company_name', 'Unknown')}: {e}")
        return 0, 0, "10", "Unable to calculate metrics - date error"
    except Exception as e:
        logger.error(f"Error calculating metrics for {ipo.get('company_name', 'Unknown')}: {e}")
        return 0, 0, "10", "Unable to calculate metrics"