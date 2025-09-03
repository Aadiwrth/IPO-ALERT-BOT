#!/usr/bin/env python3
"""
IPO Alert Bot - Main Application
Monitors IPO openings and sends email/Discord alerts
"""

import sys
import time
import threading
import asyncio
from datetime import timedelta

# Import all modules
from config import validate_environment, CHECK_INTERVAL_HOURS, logger
from utils import get_nepal_time
from function.file_watcher import FileWatcher
from function.ipo_processor import IPOProcessor
from function.discord_integration import discord_integration
from function.test_service import test_all_connections, send_startup_notification, send_error_notification


def start_discord_bot():
    """Start Discord bot in a separate thread"""
    try:
        discord_integration.start_bot()
    except Exception as e:
        logger.error(f"Discord bot error: {e}")


def wait_for_discord_ready(timeout=30):
    """Wait for Discord bot to be ready"""
    start_time = time.time()
    while not discord_integration.is_ready() and (time.time() - start_time) < timeout:
        logger.info("Waiting for Discord bot to be ready...")
        time.sleep(2)
    
    if discord_integration.is_ready():
        logger.info("Discord bot is ready!")
        return True
    else:
        logger.warning("Discord bot failed to start within timeout")
        return False


def main():
    """Main application entry point"""
    
    # Validate environment variables
    if not validate_environment():
        logger.error("Environment validation failed. Exiting.")
        sys.exit(1)
    
    # Test connections before starting
    if not test_all_connections():
        logger.error("Connection tests failed. Please check your configuration.")
        send_error_notification("Connection tests failed during startup", is_fatal=True)
        sys.exit(1)
    
    # Initialize IPO processor
    ipo_processor = IPOProcessor()
    
    logger.info("=== IPO Alert Bot Started ===")
    logger.info(f"Check interval: {CHECK_INTERVAL_HOURS} hours")
    logger.info("=====================================")
    
    try:
        # Start Discord bot in background thread
        discord_thread = threading.Thread(target=start_discord_bot, daemon=True)
        discord_thread.start()
        
        # Wait for Discord bot to be ready
        discord_ready = wait_for_discord_ready()
        
        # Send Discord startup notification if ready
        if discord_ready:
            try:
                asyncio.run_coroutine_threadsafe(
                    discord_integration.send_system_notification(
                        "Bot Startup",
                        "✅ The IPO Alert Bot is online and ready to send notifications.",
                        "success"
                    ),
                    discord_integration.get_loop()
                ).result(timeout=5)
            except Exception as e:
                logger.warning(f"Failed to send Discord startup notification: {e}")
        
        # Send email startup notification
        send_startup_notification()
        
        # Start file watcher for email list updates
        with FileWatcher(callback=ipo_processor.update_email_list):
            
            # Main processing loop
            while True:
                try:
                    # Process IPO alerts
                    ipo_processor.process_ipo_alerts()
                    
                    # Calculate next check time
                    next_check = ipo_processor.get_next_check_time(CHECK_INTERVAL_HOURS)
                    logger.info(f"Next check scheduled at: {next_check.strftime('%Y-%m-%d %H:%M:%S')} NPT")
                    logger.info(f"Sleeping for {CHECK_INTERVAL_HOURS} hours...")
                    
                    # Sleep until next check
                    time.sleep(CHECK_INTERVAL_HOURS * 3600)
                    
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}")
                    send_error_notification(str(e), is_fatal=False)
                    
                    # Send Discord error notification if available
                    if discord_integration.is_ready():
                        try:
                            asyncio.run_coroutine_threadsafe(
                                discord_integration.send_system_notification(
                                    "Bot Error",
                                    f"⚠️ An error occurred: `{str(e)}`\nContinuing after 5 minutes...",
                                    "error"
                                ),
                                discord_integration.get_loop()
                            )
                        except Exception as discord_error:
                            logger.error(f"Failed to send Discord error notification: {discord_error}")
                    
                    logger.info("Continuing after error...")
                    time.sleep(300)  # Retry after 5 minutes
    
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        send_error_notification(str(e), is_fatal=True)
        
        # Send Discord fatal error notification if available
        if discord_integration.is_ready():
            try:
                asyncio.run_coroutine_threadsafe(
                    discord_integration.send_system_notification(
                        "Fatal Error",
                        f"❌ Bot encountered a fatal error and is shutting down: `{str(e)}`",
                        "error"
                    ),
                    discord_integration.get_loop()
                ).result(timeout=5)
            except Exception:
                pass  # Don't let Discord errors prevent shutdown
        
        sys.exit(1)
    
    finally:
        # Cleanup
        logger.info("Shutting down...")
        if discord_integration.is_ready():
            try:
                asyncio.run_coroutine_threadsafe(
                    discord_integration.close(),
                    discord_integration.get_loop()
                ).result(timeout=5)
            except Exception as e:
                logger.warning(f"Error closing Discord bot: {e}")
        
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()