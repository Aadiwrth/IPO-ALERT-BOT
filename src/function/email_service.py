import time
import threading
import httpx
from config import API_KEY, FROM_NAME, FROM_EMAIL, logger


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


def send_email_async(email, subject, content, is_system_notification=False):
    """Send email asynchronously"""
    threading.Thread(
        target=send_email, 
        args=(email, subject, content, is_system_notification)
    ).start()


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