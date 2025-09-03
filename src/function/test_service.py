from ..config import ADMIN_EMAIL, EMAIL_LIST_FILE, CHECK_INTERVAL_HOURS, logger
from ..utils import load_email_list
from .api_service import test_api_connection
from .email_service import send_email
from .email_templates import create_system_notification_email


def test_all_connections():
    """Test API and email connectivity"""
    logger.info("Testing connections...")
    
    # Load and display email list
    email_list = load_email_list()
    logger.info(f"Email list contains {len(email_list)} addresses")
    
    # Test API
    api_success = test_api_connection()
    if not api_success:
        return False
    
    # Test email (send test notification to admin only)
    email_success = test_email_connection(len(email_list))
    return email_success


def test_email_connection(subscriber_count):
    """Test email connectivity by sending a test to admin"""
    try:
        test_subject = "IPO Bot Test - Connection Verified"
        test_message = f"""IPO Alert Bot is working correctly!<br><br>
<strong>Configuration:</strong><br>
• Email list file: {EMAIL_LIST_FILE}<br>
• Subscribers: {subscriber_count} email addresses<br>
• Check interval: {CHECK_INTERVAL_HOURS} hours<br>
• API endpoint: Connected successfully"""
        
        test_body = create_system_notification_email(
            "Connection Test", 
            test_message, 
            "info"
        )
        
        success = send_email(ADMIN_EMAIL, test_subject, test_body, True)
        if success:
            logger.info("✓ Email test sent successfully to admin")
            return True
        else:
            logger.error("✗ Email test failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Email test failed: {e}")
        return False


def send_startup_notification():
    """Send startup notification to admin"""
    try:
        startup_subject = "IPO Alert Bot Started"
        startup_message = f"""✓ Bot is now monitoring IPO openings every {CHECK_INTERVAL_HOURS} hours<br>
✓ Using Nepal Time Zone (NPT)<br>
✓ Email list file: {EMAIL_LIST_FILE}<br>
✓ Ready to send alerts when IPOs open"""
        
        startup_body = create_system_notification_email(
            "IPO Alert Bot Status",
            startup_message,
            "success"
        )
        
        return send_email(ADMIN_EMAIL, startup_subject, startup_body, True)
        
    except Exception as e:
        logger.error(f"Error sending startup notification: {e}")
        return False


def send_error_notification(error_message, is_fatal=False):
    """Send error notification to admin"""
    try:
        error_type = "Fatal Error" if is_fatal else "Bot Error"
        error_subject = f"IPO Alert Bot {error_type}"
        
        if is_fatal:
            full_message = f"IPO Alert Bot encountered a fatal error and stopped:<br><br><code>{error_message}</code><br><br>Please check the logs and restart the bot."
        else:
            full_message = f"IPO Alert Bot encountered an error and will attempt to continue:<br><br><code>{error_message}</code>"
        
        error_body = create_system_notification_email(error_type, full_message, "error")
        return send_email(ADMIN_EMAIL, error_subject, error_body, True)
        
    except Exception as e:
        logger.error(f"Error sending error notification: {e}")
        return False