#!/usr/bin/env python3
"""
LinkedIn Watcher - Monitors LinkedIn and creates posts for business promotion.

This watcher:
1. Creates scheduled posts based on business goals
2. Monitors LinkedIn for engagement opportunities
3. Creates action files in Needs_Action for Qwen to process

Note: LinkedIn automation should be used carefully to comply with LinkedIn ToS.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
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


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for engagement opportunities and creates scheduled posts.
    
    Creates action files for:
    - Scheduled business posts
    - Engagement opportunities (comments on relevant posts)
    - Connection requests to follow up
    """
    
    def __init__(self, vault_path: str = None, session_path: str = None, check_interval: int = None):
        """
        Initialize LinkedIn watcher.

        Args:
            vault_path: Path to Obsidian vault (default: from env VAULT_PATH)
            session_path: Path to store browser session (default: from env LINKEDIN_SESSION_PATH)
            check_interval: Seconds between checks (default: from env LINKEDIN_CHECK_INTERVAL or 300)
        """
        # Use environment variables if not provided
        if vault_path is None:
            vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
        if check_interval is None:
            check_interval = int(os.getenv('LINKEDIN_CHECK_INTERVAL', '300'))
        
        super().__init__(vault_path, check_interval)

        self.session_path = Path(session_path or os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Post templates for business promotion
        self.post_templates = [
            {
                'type': 'thought_leadership',
                'template': """💡 Industry Insight:

{insight}

What we're seeing in {industry}:
• {point1}
• {point2}
• {point3}

The future is {trend}. Is your business ready?

#ThoughtLeadership #{industry_tag} #FutureOfWork""",
            },
            {
                'type': 'product_update',
                'template': """🚀 Exciting Update!

We're thrilled to announce {product_name} - {brief_description}.

After {development_time} of development, we're ready to help businesses like yours {key_benefit}.

👉 Learn more: {link}

#Innovation #ProductLaunch #{industry_tag}""",
            },
            {
                'type': 'customer_success',
                'template': """🎉 Customer Success Story!

Helped {client_type} achieve {impressive_result} using our solution.

"{testimonial}" - {client_name}

Ready for similar results? Let's talk!

#CustomerSuccess #Results #Testimonial""",
            },
        ]
        
        # Load posted content log
        self._load_posted_log()
    
    def _load_posted_log(self):
        """Load list of posted content."""
        log_file = self.vault_path / 'Logs' / 'linkedin_posted.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                self.posted_content = set(line.strip() for line in f.readlines()[-100:])
        else:
            self.posted_content = set()
    
    def _save_to_log(self, content_hash: str):
        """Save posted content hash to log."""
        log_file = self.vault_path / 'Logs' / 'linkedin_posted.log'
        with open(log_file, 'a') as f:
            f.write(f"{content_hash}\n")
    
    def _generate_post_content(self, post_type: str, **kwargs) -> str:
        """Generate post content from template."""
        for template in self.post_templates:
            if template['type'] == post_type:
                return template['template'].format(**kwargs)
        return ""
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check for post opportunities.
        
        Returns:
            List of post opportunity dictionaries
        """
        opportunities = []
        
        # Check business goals for content ideas (UTF-8 encoding for emoji support)
        business_goals = self.vault_path / 'Business_Goals.md'
        if business_goals.exists():
            content = business_goals.read_text(encoding='utf-8')
            
            # Check if we should post (e.g., Tuesday-Thursday, 10 AM)
            now = datetime.now()
            should_post = now.weekday() in [1, 2, 3] and 9 <= now.hour <= 11  # Tue-Thu, 9-11 AM
            
            if should_post:
                # Generate post based on goals
                post_opportunity = {
                    'type': 'scheduled_post',
                    'priority': 'normal',
                    'suggested_time': now.isoformat(),
                    'content_ideas': self._extract_content_ideas(content),
                }
                
                # Create unique hash
                content_hash = f"scheduled_{now.strftime('%Y%m%d')}"
                if content_hash not in self.posted_content:
                    opportunities.append(post_opportunity)
        
        return opportunities
    
    def _extract_content_ideas(self, business_goals_content: str) -> List[str]:
        """Extract content ideas from business goals."""
        ideas = []
        
        # Look for active projects
        if 'Active Projects' in business_goals_content:
            ideas.append("Share update on active projects")
        
        # Look for revenue targets
        if 'Revenue' in business_goals_content:
            ideas.append("Share business milestone or achievement")
        
        # Default ideas
        if not ideas:
            ideas = [
                "Share industry insight",
                "Post customer success story",
                "Announce product update"
            ]
        
        return ideas
    
    def create_action_file(self, opportunity: Dict) -> Optional[Path]:
        """
        Create action file for LinkedIn opportunity.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            Path to created file
        """
        if opportunity['type'] == 'scheduled_post':
            filename = self.generate_filename('LINKEDIN', 'post')
            filepath = self.needs_action / filename
            
            content = f"""{self.create_frontmatter(
                item_type='linkedin_post',
                priority=opportunity.get('priority', 'normal'),
                suggested_time=opportunity.get('suggested_time', ''),
                status='pending'
            )}

## LinkedIn Post Opportunity

**Type:** Scheduled Business Post
**Suggested Time:** {opportunity.get('suggested_time', 'ASAP')}
**Priority:** {opportunity.get('priority', 'normal')}

## Content Ideas

"""
            for idea in opportunity.get('content_ideas', []):
                content += f"- {idea}\n"
            
            content += f"""

## Suggested Actions

- [ ] Draft post content
- [ ] Review against Company Handbook
- [ ] Create approval request (HITL required)
- [ ] Schedule or publish post

## Post Templates

### Thought Leadership
```
💡 Industry Insight:

[Your insight about industry trend]

What we're seeing:
• Point 1
• Point 2  
• Point 3

The future is [trend]. Is your business ready?

#ThoughtLeadership #Industry #FutureOfWork
```

### Product Update
```
🚀 Exciting Update!

We're thrilled to announce [product] - [description].

After [time] of development, we're ready to help businesses like yours [benefit].

👉 Learn more: [link]

#Innovation #ProductLaunch
```

### Customer Success
```
🎉 Customer Success Story!

Helped [client] achieve [result] using our solution.

"[Testimonial]" - [Client Name]

Ready for similar results? Let's talk!

#CustomerSuccess #Results
```

## Notes

```
Add draft content here
```

---
*Detected by LinkedInWatcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Requires human approval before posting (HITL)*
"""
            
            filepath.write_text(content)
            
            # Log as posted (to avoid duplicates today)
            content_hash = f"scheduled_{datetime.now().strftime('%Y%m%d')}"
            self.posted_content.add(content_hash)
            self._save_to_log(content_hash)
            
            return filepath
        
        return None


class LinkedInPoster:
    """
    LinkedIn poster using Playwright for browser automation.
    
    Usage:
        poster = LinkedInPoster()
        poster.login()
        poster.create_post("Hello LinkedIn!")
        poster.close()
    """
    
    def __init__(self, session_path: str = None):
        """Initialize LinkedIn poster."""
        self.session_path = Path(session_path or './linkedin_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        self._playwright = None
        self._browser = None
        self._page = None
    
    def _init_browser(self):
        """Initialize browser."""
        if self._playwright is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=False,  # Show browser for login
                args=['--disable-blink-features=AutomationControlled']
            )
            self._page = self._browser.pages[0]
    
    def login(self):
        """Login to LinkedIn."""
        self._init_browser()
        
        print("\n📱 LinkedIn Login")
        print("=" * 50)
        print("1. Browser will open")
        print("2. Navigate to LinkedIn login")
        print("3. Complete login manually")
        print("4. Session will be saved for future use")
        
        self._page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
        
        # Wait for user to login
        print("\nWaiting for login (max 2 minutes)...")
        try:
            # Wait for feed page (indicates successful login)
            self._page.wait_for_url('**/feed/**', timeout=120000)
            print("✓ Login successful!")
            return True
        except PlaywrightTimeout:
            print("⚠ Login timeout - may need manual intervention")
            return False
    
    def create_post(self, content: str, image_path: str = None) -> bool:
        """Create a LinkedIn post."""
        if not self._page:
            self._init_browser()
        
        try:
            print("\n📝 Creating LinkedIn post...")
            
            # Navigate to feed
            self._page.goto('https://www.linkedin.com/feed', wait_until='domcontentloaded')
            time.sleep(2)
            
            # Click start post button
            try:
                start_post_btn = self._page.locator('[aria-label="Start a post"]').first
                start_post_btn.click()
                time.sleep(1)
            except Exception as e:
                print(f"⚠ Could not find post button: {e}")
                return False
            
            # Find text input and type content
            text_input = self._page.locator('[contenteditable="true"]').first
            text_input.fill(content)
            time.sleep(0.5)
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                try:
                    media_btn = self._page.locator('[aria-label*="photo"]').first
                    media_btn.click()
                    time.sleep(0.5)
                    
                    file_input = self._page.locator('input[type="file"]').first
                    file_input.set_input_files(image_path)
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠ Could not attach image: {e}")
            
            # Click post button
            post_btn = self._page.locator('button:has-text("Post")').first
            post_btn.click()
            time.sleep(2)
            
            print("✓ Post created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create post: {e}")
            return False
    
    def close(self):
        """Close browser."""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None


def main():
    """Run the LinkedIn watcher."""
    # Use environment variable or command line argument
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    # Check interval from environment or default (5 minutes = 300 seconds)
    check_interval = int(os.getenv('LINKEDIN_CHECK_INTERVAL', '300'))

    watcher = LinkedInWatcher(vault_path, check_interval=check_interval)
    watcher.run()


if __name__ == '__main__':
    main()
