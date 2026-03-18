#!/usr/bin/env python3
"""
WhatsApp Watcher - Monitors WhatsApp Web for urgent messages.

This watcher uses Playwright to automate WhatsApp Web and check for:
- Unread messages
- Messages containing urgent keywords
- Messages from important contacts

When matching messages are found, action files are created in Needs_Action folder.

Note: Be aware of WhatsApp's Terms of Service when using automation.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Missing dependencies. Install with:")
    print("pip install playwright")
    print("playwright install chromium")
    sys.exit(1)

from base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for urgent messages.
    
    Creates action files in Needs_Action folder for messages containing
    urgent keywords like: urgent, asap, invoice, payment, help
    """
    
    def __init__(self, vault_path: str = None, session_path: str = None, check_interval: int = None):
        """
        Initialize WhatsApp watcher.

        Args:
            vault_path: Path to Obsidian vault (default: from env VAULT_PATH)
            session_path: Path to store browser session (default: from env WHATSAPP_SESSION_PATH)
            check_interval: Seconds between checks (default: from env WHATSAPP_CHECK_INTERVAL or 30)
        """
        # Use environment variables if not provided
        if vault_path is None:
            vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
        if check_interval is None:
            check_interval = int(os.getenv('WHATSAPP_CHECK_INTERVAL', '30'))
        
        super().__init__(vault_path, check_interval)

        self.session_path = Path(session_path or os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session'))
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Keywords that indicate urgency
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'quote', 'deadline']
        
        # Load processed message IDs from log
        self._load_processed_log()
        
        # Browser context
        self._context = None
        self._page = None
    
    def _load_processed_log(self):
        """Load list of processed message IDs."""
        log_file = self.vault_path / 'Logs' / 'processed_whatsapp.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                # Load last 1000 entries to prevent unbounded growth
                lines = f.readlines()[-1000:]
                self.processed_ids = set(line.strip() for line in lines if line.strip())
        else:
            self.processed_ids = set()
    
    def _save_to_log(self, msg_id: str):
        """Save processed message ID to log."""
        log_file = self.vault_path / 'Logs' / 'processed_whatsapp.log'
        with open(log_file, 'a') as f:
            f.write(f"{msg_id}\n")
    
    def _init_browser(self):
        """Initialize browser with persistent context."""
        if self._context is not None:
            return
        
        playwright = sync_playwright().start()
        self._context = playwright.chromium.launch_persistent_context(
            self.session_path,
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        self._page = self._context.pages[0]
        self.logger.info("Browser initialized")
    
    def _close_browser(self):
        """Close browser."""
        if self._context:
            self._context.close()
            self._context = None
            self._page = None
    
    def _is_whatsapp_loaded(self) -> bool:
        """Check if WhatsApp Web is loaded."""
        try:
            # Check for chat list (main WhatsApp Web element)
            self._page.wait_for_selector('[data-testid="chat-list"]', timeout=5000)
            return True
        except PlaywrightTimeout:
            return False
    
    def _needs_qr_scan(self) -> bool:
        """Check if QR code scan is needed."""
        try:
            # Look for QR code element
            qr = self._page.query_selector('[data-testid="qr-icon"]')
            return qr is not None
        except:
            return False
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check for new urgent messages.
        
        Returns:
            List of message data dictionaries
        """
        try:
            self._init_browser()
            
            # Navigate to WhatsApp Web
            self._page.goto('https://web.whatsapp.com', wait_until='domcontentloaded')
            
            # Wait for chat list (may need QR scan first time)
            try:
                self._page.wait_for_selector('[data-testid="chat-list"]', timeout=15000)
            except PlaywrightTimeout:
                self.logger.warning("WhatsApp Web not loaded. May need QR scan.")
                self.logger.warning(f"Open WhatsApp Web manually in: {self.session_path}")
                return []
            
            # Find unread messages
            unread_chats = self._page.query_selector_all('[aria-label*="unread"], [data-testid="unread-mark"]')
            
            messages = []
            for chat in unread_chats:
                try:
                    # Get chat name/number
                    chat_name_elem = chat.query_selector('[data-testid="chat-cell-title"]')
                    chat_name = chat_name_elem.inner_text() if chat_name_elem else 'Unknown'
                    
                    # Get last message
                    message_elem = chat.query_selector('[data-testid="chat-cell-subtitle"]')
                    message_text = message_elem.inner_text() if message_elem else ''
                    
                    # Check for keywords
                    message_lower = message_text.lower()
                    if any(keyword in message_lower for keyword in self.keywords):
                        # Create unique ID
                        msg_id = f"{chat_name}_{message_text[:20]}_{datetime.now().strftime('%Y%m%d%H%M')}"
                        
                        if msg_id not in self.processed_ids:
                            messages.append({
                                'id': msg_id,
                                'from': chat_name,
                                'message': message_text,
                                'timestamp': datetime.now().isoformat()
                            })
                except Exception as e:
                    self.logger.debug(f"Error processing chat: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            self.logger.error(f"WhatsApp check failed: {e}")
            self._close_browser()
            return []
        finally:
            # Close browser to save resources
            self._close_browser()
    
    def create_action_file(self, message: Dict) -> Optional[Path]:
        """
        Create action file for WhatsApp message.
        
        Args:
            message: Message data dictionary
            
        Returns:
            Path to created file
        """
        filename = self.generate_filename('WHATSAPP', message['id'][:10].replace(' ', '_'))
        filepath = self.needs_action / filename
        
        # Determine priority
        priority = 'high' if any(k in message['message'].lower() for k in ['urgent', 'asap', 'emergency']) else 'normal'
        
        content = f"""{self.create_frontmatter(
            item_type='whatsapp_message',
            from_contact=f'"{message["from"]}"',
            received=f'"{message["timestamp"]}"',
            priority=priority,
            status='pending'
        )}

## WhatsApp Message

**From:** {message['from']}
**Received:** {message['timestamp']}
**Priority:** {priority}

---

### Message Content

{message['message']}

## Context

*Keywords detected:* {[k for k in self.keywords if k in message['message'].lower()]}

## Suggested Actions

- [ ] Read full message in WhatsApp
- [ ] Reply to contact
- [ ] Take required action
- [ ] Mark as read in WhatsApp

## Notes

```
Add notes about this message here
```

---
*Detected by WhatsAppWatcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        filepath.write_text(content)
        
        # Log as processed
        self.processed_ids.add(message['id'])
        self._save_to_log(message['id'])
        
        return filepath
    
    def run(self):
        """Main run loop."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Monitoring keywords: {self.keywords}')
        
        # First-time auth check
        self._init_browser()
        self._page.goto('https://web.whatsapp.com', wait_until='domcontentloaded')
        
        try:
            self._page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
            self.logger.info("WhatsApp session authenticated ✓")
        except PlaywrightTimeout:
            self.logger.warning("=" * 50)
            self.logger.warning("QR CODE SCAN REQUIRED")
            self.logger.warning("=" * 50)
            self.logger.warning("1. Open WhatsApp on your phone")
            self.logger.warning("2. Go to Settings > Linked Devices")
            self.logger.warning("3. Tap 'Link a Device'")
            self.logger.warning("4. Scan the QR code shown in browser")
            self.logger.warning(f"5. Browser session saved to: {self.session_path}")
            self.logger.warning("=" * 50)
            
            # Wait for user to scan
            self.logger.info("Waiting 60 seconds for QR scan...")
            time.sleep(60)
        
        self._close_browser()
        
        # Start main loop
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} urgent message(s)')
                        for item in items:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f'Created action file: {filepath.name}')
                    else:
                        self.logger.debug('No urgent messages')
                except Exception as e:
                    self.logger.error(f'Error processing messages: {e}', exc_info=True)
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise


def main():
    """Run the WhatsApp watcher."""
    # Use environment variable or command line argument
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    # Check interval from environment or default (30 seconds)
    check_interval = int(os.getenv('WHATSAPP_CHECK_INTERVAL', '30'))

    watcher = WhatsAppWatcher(vault_path, check_interval=check_interval)
    watcher.run()


if __name__ == '__main__':
    main()
