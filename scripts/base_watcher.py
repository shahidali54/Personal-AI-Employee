#!/usr/bin/env python3
"""
Base Watcher - Abstract base class for all watcher scripts.

Watchers are lightweight Python scripts that run continuously in the background,
monitoring various inputs (Gmail, WhatsApp, filesystem) and creating actionable
files for Claude Code to process.

All Watchers follow this pattern:
1. Check for new items periodically
2. Create .md files in Needs_Action folder for new items
3. Track processed items to avoid duplicates
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Subclasses must implement:
    - check_for_updates(): Return list of new items to process
    - create_action_file(item): Create .md file in Needs_Action folder
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_ids: set = set()
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items that need processing.
        
        Returns:
            List of new items (format depends on watcher type)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file for the given item.
        
        Args:
            item: Item to process (format depends on watcher type)
            
        Returns:
            Path to created file, or None if creation failed
        """
        pass
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: Type prefix (e.g., 'EMAIL', 'FILE', 'WHATSAPP')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename with .md extension
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{unique_id}_{timestamp}.md"
    
    def create_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Create YAML frontmatter for action files.
        
        Args:
            item_type: Type of item (email, file, message, etc.)
            **kwargs: Additional metadata fields
            
        Returns:
            Formatted YAML frontmatter string
        """
        lines = [
            "---",
            f"type: {item_type}",
            f"created: {datetime.now().isoformat()}",
            "status: pending",
        ]
        
        for key, value in kwargs.items():
            lines.append(f"{key}: {value}")
        
        lines.append("---")
        return "\n".join(lines)
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        
        This method runs indefinitely until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        for item in items:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f'Created action file: {filepath.name}')
                    else:
                        self.logger.debug('No new items')
                except Exception as e:
                    self.logger.error(f'Error processing items: {e}', exc_info=True)
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise


def run_watcher(watcher_class: type, vault_path: str, check_interval: int = 60):
    """
    Helper function to instantiate and run a watcher.
    
    Args:
        watcher_class: Class of watcher to instantiate
        vault_path: Path to Obsidian vault
        check_interval: Seconds between checks
    """
    import sys
    
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    
    watcher = watcher_class(vault_path, check_interval)
    watcher.run()
