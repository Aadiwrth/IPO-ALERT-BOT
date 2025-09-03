import asyncio
from datetime import timedelta
from config import logger
from utils import get_nepal_time, load_email_list, calculate_ipo_metrics
from .api_service import fetch_ipo_data
from .email_service import send_bulk_emails
from .email_templates import create_ipo_alert_email
from .discord_integration import discord_integration


class IPOProcessor:
    def __init__(self):
        self.sent_today = set()
        self.last_check_date = None
        self.email_list = []

    def update_email_list(self, new_email_list):
        """Callback for when email list file changes"""
        self.email_list = new_email_list
        logger.info(f"Email list updated: {len(self.email_list)} addresses")

    def process_ipo_alerts(self):
        """Check for IPOs opening today and send alerts"""
        nepal_time = get_nepal_time()
        today_str = nepal_time.strftime("%Y-%m-%d")
        
        logger.info(f"Checking IPO alerts for {today_str} (Nepal Time: {nepal_time.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # Reset sent_today if it's a new day
        if self.last_check_date != today_str:
            self.sent_today.clear()
            logger.info("New day detected - cleared sent emails tracker")
            self.last_check_date = today_str
        
        # Load email list for IPO alerts
        if not self.email_list:
            self.email_list = load_email_list()
        
        if not self.email_list:
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
                    if ipo_id in self.sent_today:
                        logger.info(f"Email already sent today for {company_name} ({finid})")
                        continue
                    
                    # Calculate metrics
                    rem_days, prob, sug_qty, suggestion = calculate_ipo_metrics(ipo, today_str)
                    
                    # Create email content
                    email_body = create_ipo_alert_email(ipo, rem_days, prob, sug_qty, suggestion)
                    subject = f"IPO Alert: {company_name} Now Open for Subscription"
                    
                    # Send email to all subscribers
                    successful_sends = send_bulk_emails(self.email_list, subject, email_body)
                    
                    # Send Discord alert if bot is ready
                    if discord_integration.is_ready() and discord_integration.get_loop():
                        try:
                            asyncio.run_coroutine_threadsafe(
                                discord_integration.send_ipo_alert(ipo, rem_days, prob, sug_qty, suggestion),
                                discord_integration.get_loop()
                            )
                        except Exception as e:
                            logger.error(f"Error sending Discord alert: {e}")
                    
                    # Mark as sent
                    self.sent_today.add(ipo_id)
                    alerts_sent += 1
                    
                    logger.info(f"IPO Alert sent for {company_name} ({finid}) to {successful_sends} subscribers - Probability: {prob:.1f}%")
            
            except Exception as e:
                logger.error(f"Error processing IPO {ipo.get('company_name', 'Unknown')}: {e}")
        
        if alerts_sent == 0:
            logger.info("No new IPO openings found for today")
        else:
            logger.info(f"Sent {alerts_sent} IPO alert(s) to {len(self.email_list)} subscribers")

    def get_next_check_time(self, hours=5):
        """Get the next check time"""
        return get_nepal_time() + timedelta(hours=hours)