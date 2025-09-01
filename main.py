import os
import time
import threading
import httpx
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class EmailFileHandler(FileSystemEventHandler):
    """Watch email_update.txt for changes"""
    def on_modified(self, event):
        if event.src_path.endswith(EMAIL_LIST_FILE):
            logger.info(f"{EMAIL_LIST_FILE} changed, reloading email list...")
            # Reload email list dynamically
            global email_list
            email_list = load_email_list()

# ===== SETUP LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ipo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== LOAD ENV =====
load_dotenv()

API_KEY = os.getenv("BREVO_API_KEY")
FROM_NAME = os.getenv("FROM_NAME")
FROM_EMAIL = os.getenv("FROM_EMAIL")
ADMIN_EMAIL = os.getenv("TO_EMAIL")  # Admin email for system notifications only
ONGOING_URL = os.getenv("ONGOING_URL")
TOTAL_APPS = int(os.getenv("TOTAL_APPS", 2500000))
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", 5))
EMAIL_LIST_FILE = "email_update.txt"

# Nepal timezone
NEPAL_TZ = pytz.timezone('Asia/Kathmandu')

# Track sent emails to avoid duplicates
sent_today = set()


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


def send_email(email, subject, content, is_system_notification=False):
    """Send email via Brevo API (thread safe)"""
    try:
        res = httpx.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
                "to": [{"email": email}],
                "subject": subject,
                "htmlContent": content
            },
            timeout=10
        )
        if res.status_code != 201:
            logger.error(f"Failed to send email to {email}: {res.text}")
            return False
        else:
            email_type = "system notification" if is_system_notification else "IPO alert"
            logger.info(f"Email sent successfully to {email} ({email_type})")
            return True
    except Exception as e:
        logger.error(f"Error sending email to {email}: {e}")
        return False


def send_async(email, subject, content, is_system_notification=False):
    """Send email asynchronously"""
    threading.Thread(target=send_email, args=(email, subject, content, is_system_notification)).start()


def send_bulk_emails(emails, subject, content):
    """Send emails to multiple recipients"""
    if not emails:
        logger.warning("No email addresses to send to")
        return 0
    
    successful_sends = 0
    for email in emails:
        if send_email(email, subject, content):
            successful_sends += 1
        time.sleep(0.5)  # Small delay to avoid rate limiting
    
    logger.info(f"Bulk email sent: {successful_sends}/{len(emails)} successful")
    return successful_sends


def send_bulk_emails_async(emails, subject, content):
    """Send bulk emails asynchronously"""
    threading.Thread(target=send_bulk_emails, args=(emails, subject, content)).start()


def create_email_body(ipo, rem_days, prob, sug_qty, suggestion):
    """Create professional HTML email body for IPO alerts"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPO Alert</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8f9fa;">
    
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 40px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: -0.5px;">
                IPO Opening Alert
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 14px;">
                Investment Opportunity Notification
            </p>
        </div>

        <!-- Main Content -->
        <div style="padding: 40px;">
            
            <!-- Company Alert -->
            <div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 20px; margin-bottom: 30px; border-radius: 0 8px 8px 0;">
                <h2 style="color: #1976d2; margin: 0 0 8px 0; font-size: 20px; font-weight: 600;">
                    {ipo['company_name']}
                </h2>
                <p style="color: #424242; margin: 0; font-size: 14px;">
                    IPO is now open for subscription
                </p>
            </div>

            <!-- IPO Details -->
            <div style="margin-bottom: 30px;">
                <h3 style="color: #333; margin: 0 0 20px 0; font-size: 18px; font-weight: 600; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;">
                    Issue Details
                </h3>
                
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; width: 40%; border-bottom: 1px solid #f5f5f5;">
                            Company
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['company_name']}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Symbol
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['finid']}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Sector
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo.get('Sector', 'N/A')}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Offer Price
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            NPR {ipo.get('offer_price', 'N/A')}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Opening Date
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['open_date'].split(' ')[0]}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Closing Date
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['close_date'].split(' ')[0]}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Days Remaining
                        </td>
                        <td style="padding: 12px 0; color: #e65100; font-weight: 700; border-bottom: 1px solid #f5f5f5;">
                            {rem_days} day{'s' if rem_days != 1 else ''}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500; border-bottom: 1px solid #f5f5f5;">
                            Total Shares
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600; border-bottom: 1px solid #f5f5f5;">
                            {ipo['shares_offered']:,}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #666; font-weight: 500;">
                            Issue Manager
                        </td>
                        <td style="padding: 12px 0; color: #333; font-weight: 600;">
                            {ipo.get('issue_manager', 'N/A')}
                        </td>
                    </tr>
                </table>
            </div>

            <!-- Investment Analysis -->
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                <h3 style="color: #333; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">
                    Investment Analysis
                </h3>
                
                <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                    <div style="flex: 1; min-width: 200px;">
                        <p style="margin: 0 0 8px 0; color: #666; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                            Allotment Probability
                        </p>
                        <p style="margin: 0; font-size: 24px; font-weight: 700; color: {'#4caf50' if prob >= 50 else '#ff9800' if prob >= 20 else '#f44336'};">
                            {prob:.1f}%
                        </p>
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <p style="margin: 0 0 8px 0; color: #666; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                            Recommended Quantity
                        </p>
                        <p style="margin: 0; font-size: 24px; font-weight: 700; color: #333;">
                            {sug_qty} units
                        </p>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background-color: #ffffff; border-radius: 6px; border-left: 3px solid #2196f3;">
                    <p style="margin: 0; color: #555; font-size: 14px; line-height: 1.5;">
                        <strong>Recommendation:</strong> {suggestion}
                    </p>
                </div>
            </div>

            <!-- Action Note -->
            <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; border-left: 3px solid #ff9800;">
                <p style="margin: 0; color: #e65100; font-size: 14px; font-weight: 500;">
                    <strong>Action Required:</strong> IPO subscription window is now open. Please review and submit your application through your broker.
                </p>
            </div>

        </div>

        <!-- Footer -->
        <div style="background-color: #f5f5f5; padding: 25px 40px; text-align: center; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0 0 10px 0; color: #666; font-size: 12px;">
                This analysis is based on estimated total applications of {TOTAL_APPS:,}
            </p>
            <p style="margin: 0 0 10px 0; color: #666; font-size: 12px;">
                Automated IPO Alert System • Last checked: {get_nepal_time().strftime('%Y-%m-%d %H:%M:%S')} NPT
            </p>
            <p style="margin: 0; color: #999; font-size: 11px;">
                You received this because you're subscribed to IPO alerts
            </p>
        </div>

    </div>
</body>
</html>
"""


def create_system_notification_body(title, message, status_type="info"):
    """Create HTML body for system notifications (startup, test, error)"""
    color_map = {
        "success": {"bg": "#e8f5e8", "border": "#4caf50", "text": "#2e7d32"},
        "info": {"bg": "#e3f2fd", "border": "#2196f3", "text": "#1565c0"},
        "warning": {"bg": "#fff3e0", "border": "#ff9800", "text": "#e65100"},
        "error": {"bg": "#ffebee", "border": "#f44336", "text": "#c62828"}
    }
    
    colors = color_map.get(status_type, color_map["info"])
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h2 style="color: {colors['text']}; margin: 0 0 20px 0;">{title}</h2>
        <div style="background-color: {colors['bg']}; padding: 15px; border-radius: 6px; border-left: 3px solid {colors['border']};">
            <p style="margin: 0; color: {colors['text']}; line-height: 1.5;">
                {message}
            </p>
        </div>
        <p style="margin: 15px 0 0 0; color: #666; font-size: 12px;">
            Timestamp: {get_nepal_time().strftime('%Y-%m-%d %H:%M:%S')} NPT
        </p>
    </div>
</body>
</html>
"""


def fetch_ipo_data():
    """Fetch IPO data from API"""
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(ONGOING_URL)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Successfully fetched IPO data - {len(data.get('response', []))} IPOs found")
            return data.get("response", [])
    except httpx.TimeoutException:
        logger.error("Timeout while fetching IPO data")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while fetching IPO data: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching IPO data: {e}")
        return []


def process_ipo_alerts():
    """Check for IPOs opening today and send alerts"""
    global sent_today
    
    nepal_time = get_nepal_time()
    today_str = nepal_time.strftime("%Y-%m-%d")
    
    logger.info(f"Checking IPO alerts for {today_str} (Nepal Time: {nepal_time.strftime('%Y-%m-%d %H:%M:%S')})")
    
    # Reset sent_today if it's a new day
    if hasattr(process_ipo_alerts, 'last_check_date'):
        if process_ipo_alerts.last_check_date != today_str:
            sent_today.clear()
            logger.info("New day detected - cleared sent emails tracker")
    
    process_ipo_alerts.last_check_date = today_str
    
    # Load email list for IPO alerts
    email_list = load_email_list()
    if not email_list:
        logger.warning("No email addresses loaded from email_update.txt - no IPO alerts will be sent")
        return
    
    ipo_data = fetch_ipo_data()
    
    if not ipo_data:
        logger.warning("No IPO data received or API error")
        return
    
    alerts_sent = 0
    
    for ipo in ipo_data:
        try:
            # Extract date from open_date (format: "2025-09-01 00:00:00")
            open_date = ipo.get("open_date", "").split(" ")[0] if ipo.get("open_date") else None
            close_date = ipo.get("close_date", "").split(" ")[0] if ipo.get("close_date") else None
            
            if not open_date or not close_date:
                logger.warning(f"Missing date info for IPO: {ipo.get('company_name', 'Unknown')}")
                continue
            
            # Check if IPO opens today
            if open_date == today_str:
                company_name = ipo.get('company_name', 'Unknown Company')
                finid = ipo.get('finid', 'N/A')
                
                # Create unique identifier for this IPO
                ipo_id = f"{finid}_{open_date}"
                
                # Skip if already sent today
                if ipo_id in sent_today:
                    logger.info(f"Email already sent today for {company_name} ({finid})")
                    continue
                
                # Calculate remaining days
                try:
                    close_datetime = datetime.strptime(close_date, "%Y-%m-%d")
                    current_datetime = datetime.strptime(today_str, "%Y-%m-%d")
                    rem_days = (close_datetime - current_datetime).days
                except ValueError as e:
                    logger.error(f"Date parsing error for {company_name}: {e}")
                    rem_days = 0
                
                # Calculate probability and suggestions
                shares_offered = ipo.get('shares_offered', 0)
                prob = (shares_offered / TOTAL_APPS) * 100 if shares_offered > 0 else 0
                
                sug_qty = "10" if prob < 90 else "more than 10"
                suggestion = (
                    "Conservative approach recommended due to high demand."
                    if prob < 90
                    else "Higher allocation possible due to favorable probability."
                )
                
                # Create email content
                email_body = create_email_body(ipo, rem_days, prob, sug_qty, suggestion)
                subject = f"IPO Alert: {company_name} Now Open for Subscription"
                
                # Send email to all subscribers
                successful_sends = send_bulk_emails(email_list, subject, email_body)
                
                # Mark as sent
                sent_today.add(ipo_id)
                alerts_sent += 1
                
                logger.info(f"IPO Alert sent for {company_name} ({finid}) to {successful_sends} subscribers - Probability: {prob:.1f}%")
        
        except Exception as e:
            logger.error(f"Error processing IPO {ipo.get('company_name', 'Unknown')}: {e}")
    
    if alerts_sent == 0:
        logger.info("No new IPO openings found for today")
    else:
        logger.info(f"Sent {alerts_sent} IPO alert(s) to {len(email_list)} subscribers")


def run_bot():
    """Main bot loop - runs continuously"""
    global email_list
    email_list = load_email_list()  # Load initially

    # Start file watcher
    event_handler = EmailFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    
    logger.info("=== IPO Alert Bot Started ===")
    logger.info(f"Watching {EMAIL_LIST_FILE} for updates...")
    
    try:
        while True:
            try:
                process_ipo_alerts()  # This uses the latest email_list
                
                # Sleep for the interval
                next_check = get_nepal_time() + timedelta(hours=CHECK_INTERVAL_HOURS)
                logger.info(f"Next check scheduled at: {next_check.strftime('%Y-%m-%d %H:%M:%S')} NPT")
                time.sleep(CHECK_INTERVAL_HOURS * 3600)
            
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(300)  # Retry after 5 minutes
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    finally:
        observer.stop()
        observer.join()
        
    logger.info("=== IPO Alert Bot Started ===")
    logger.info(f"Check interval: {CHECK_INTERVAL_HOURS} hours")
    logger.info(f"Nepal timezone: {NEPAL_TZ}")
    logger.info(f"Admin email: {ADMIN_EMAIL}")
    logger.info(f"Email list file: {EMAIL_LIST_FILE}")
    logger.info("=====================================")
    
    # Send startup notification to admin only
    startup_subject = "IPO Alert Bot Started"
    startup_message = f"""✓ Bot is now monitoring IPO openings every {CHECK_INTERVAL_HOURS} hours<br>
✓ Using Nepal Time Zone (NPT)<br>
✓ Email list file: {EMAIL_LIST_FILE}<br>
✓ Ready to send alerts when IPOs open"""
    
    startup_body = create_system_notification_body(
        "IPO Alert Bot Status", 
        startup_message, 
        "success"
    )
    # send_async(ADMIN_EMAIL, startup_subject, startup_body, True)
    
    while True:
        try:
            process_ipo_alerts()
            
            # Calculate next check time
            next_check = get_nepal_time() + timedelta(hours=CHECK_INTERVAL_HOURS)
            logger.info(f"Next check scheduled at: {next_check.strftime('%Y-%m-%d %H:%M:%S')} NPT")
            logger.info(f"Sleeping for {CHECK_INTERVAL_HOURS} hours...")
            
            # Sleep for the specified interval
            time.sleep(CHECK_INTERVAL_HOURS * 3600)  # Convert hours to seconds
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user (Ctrl+C)")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            
            # Send error notification to admin only
            error_subject = "IPO Alert Bot Error"
            error_message = f"IPO Alert Bot encountered an error and will attempt to continue:<br><br><code>{str(e)}</code>"
            error_body = create_system_notification_body(
                "Bot Error", 
                error_message, 
                "error"
            )
            # send_async(ADMIN_EMAIL, error_subject, error_body, True)
            
            logger.info("Continuing after error...")
            time.sleep(300)  # Wait 5 minutes before retrying


def test_connection():
    """Test API and email connectivity"""
    logger.info("Testing connections...")
    
    # Load and display email list
    email_list = load_email_list()
    logger.info(f"Email list contains {len(email_list)} addresses")
    
    # Test API
    try:
        ipo_data = fetch_ipo_data()
        if ipo_data:
            logger.info(f"✓ API connection successful - {len(ipo_data)} IPOs found")
        else:
            logger.warning("✗ API connection failed or no data")
            return False
    except Exception as e:
        logger.error(f"✗ API test failed: {e}")
        return False
    
    # Test email (send test notification to admin only)
    try:
        test_subject = "IPO Bot Test - Connection Verified"
        test_message = f"""IPO Alert Bot is working correctly!<br><br>
<strong>Configuration:</strong><br>
• Email list file: {EMAIL_LIST_FILE}<br>
• Subscribers: {len(email_list)} email addresses<br>
• Check interval: {CHECK_INTERVAL_HOURS} hours<br>
• API endpoint: Connected successfully"""
        
        test_body = create_system_notification_body(
            "Connection Test", 
            test_message, 
            "info"
        )
        send_email(ADMIN_EMAIL, test_subject, test_body, True)
        logger.info("✓ Email test sent successfully to admin")
        return True
    except Exception as e:
        logger.error(f"✗ Email test failed: {e}")
        return False


if __name__ == "__main__":
    # Validate environment variables
    required_vars = ["BREVO_API_KEY", "FROM_NAME", "FROM_EMAIL", "TO_EMAIL", "ONGOING_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file")
        exit(1)
    
    # Test connections before starting
    if not test_connection():
        logger.error("Connection tests failed. Please check your configuration.")
        
        # Send error notification to admin
        error_subject = "IPO Alert Bot Startup Failed"
        error_message = "IPO Alert Bot failed to start due to connection issues. Please check your configuration and logs."
        error_body = create_system_notification_body(
            "Startup Failed", 
            error_message, 
            "error"
        )
        send_email(ADMIN_EMAIL, error_subject, error_body, True)
        exit(1)
    
    # Start the bot
    try:
        run_bot()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        
        # Send error notification to admin
        error_subject = "IPO Alert Bot Fatal Error"
        error_message = f"IPO Alert Bot encountered a fatal error and stopped:<br><br><code>{str(e)}</code><br><br>Please check the logs and restart the bot."
        error_body = create_system_notification_body(
            "Fatal Error", 
            error_message, 
            "error"
        )
        send_email(ADMIN_EMAIL, error_subject, error_body, True)
        exit(1)