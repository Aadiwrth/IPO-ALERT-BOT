from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ..config import EMAIL_LIST_FILE, logger
from ..utils import load_email_list


class EmailFileHandler(FileSystemEventHandler):
    """Watch email_update.txt for changes"""
    def __init__(self, callback=None):
        self.callback = callback
        super().__init__()

    def on_modified(self, event):
        if event.src_path.endswith(EMAIL_LIST_FILE):
            logger.info(f"{EMAIL_LIST_FILE} changed, reloading email list...")
            # Reload email list dynamically
            new_email_list = load_email_list()
            if self.callback:
                self.callback(new_email_list)


class FileWatcher:
    def __init__(self, callback=None):
        self.observer = Observer()
        self.handler = EmailFileHandler(callback)
        self.is_running = False

    def start_watching(self):
        """Start watching the email list file"""
        if not self.is_running:
            self.observer.schedule(self.handler, path='.', recursive=False)
            self.observer.start()
            self.is_running = True
            logger.info(f"Started watching {EMAIL_LIST_FILE} for changes...")

    def stop_watching(self):
        """Stop watching the email list file"""
        if self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("Stopped file watcher")

    def __enter__(self):
        self.start_watching()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_watching()