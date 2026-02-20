"""
File System Watcher for AI Employee

This script monitors a designated drop folder and moves new files
to the Needs_Action folder for Claude Code processing.
"""

import time
import logging
from pathlib import Path
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DropFolderHandler(FileSystemEventHandler):
    """Handles file creation events in the monitored folder."""

    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for the watcher."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('watcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        source = Path(event.src_path)
        # Only process certain file types
        if source.suffix.lower() in ['.txt', '.md', '.pdf', '.docx', '.xlsx']:
            self.logger.info(f"New file detected: {source.name}")

            # Copy file to Needs_Action folder
            dest = self.needs_action / f'FILE_{source.name}'
            shutil.copy2(source, dest)
            self.logger.info(f"Copied {source.name} to Needs_Action")

            # Create metadata file
            self.create_metadata(source, dest)

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        source = Path(event.src_path)
        # Only process certain file types
        if source.suffix.lower() in ['.txt', '.md', '.pdf', '.docx', '.xlsx']:
            self.logger.info(f"File modified: {source.name}")

            # Create a notification in Needs_Action
            notification_file = self.needs_action / f'MODIFIED_FILE_{source.stem}_{int(time.time())}.md'
            notification_content = f"""---
type: file_notification
original_name: {source.name}
event_type: modified
timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

File '{source.name}' has been modified in the monitored folder.
Please review the changes and take appropriate action.
"""
            notification_file.write_text(notification_content)
            self.logger.info(f"Created notification for modified file: {notification_file.name}")

    def create_metadata(self, source: Path, dest: Path):
        """Create metadata file for the copied file."""
        import os

        meta_path = dest.with_suffix(dest.suffix + '_metadata.md')
        meta_content = f"""---
type: file_drop
original_name: {source.name}
size_bytes: {source.stat().st_size}
created_time: {time.ctime(source.stat().st_ctime)}
modified_time: {time.ctime(source.stat().st_mtime)}
destination_path: {dest.relative_to(dest.parent.parent)}
---

New file dropped for processing.

File details:
- Name: {source.name}
- Size: {source.stat().st_size} bytes
- Created: {time.ctime(source.stat().st_ctime)}
- Modified: {time.ctime(source.stat().st_mtime)}

Please review and process this file according to company guidelines.
"""
        meta_path.write_text(meta_content)


def start_watcher(vault_path: str, watch_folder: str = None):
    """
    Start the file system watcher.

    Args:
        vault_path: Path to the AI Employee vault
        watch_folder: Folder to watch for new files (defaults to Inbox)
    """
    if watch_folder is None:
        watch_folder = str(Path(vault_path) / 'Inbox')

    event_handler = DropFolderHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting file watcher for folder: {watch_folder}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping file watcher...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python filesystem_watcher.py <vault_path> [watch_folder]")
        print("Example: python filesystem_watcher.py ./AI_Employee_Vault")
        sys.exit(1)

    vault_path = sys.argv[1]
    watch_folder = sys.argv[2] if len(sys.argv) > 2 else None

    start_watcher(vault_path, watch_folder)