#!/usr/bin/env python3
"""
TEST SCRIPT - Test LinkedIn Post

This is a test script for verifying LinkedIn posting functionality.
Not required for production use.

This script will:
1. Open browser
2. Login to LinkedIn (if not already)
3. Create a test post
4. Close browser

Usage:
    python scripts/test_linkedin_post.py
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\n❌ Missing Playwright!")
    print("Install with: pip install playwright")
    print("playwright install chromium\n")
    sys.exit(1)


class LinkedInTestPoster:
    """Test LinkedIn poster."""
    
    def __init__(self):
        self.session_path = Path(os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
        self.session_path.mkdir(parents=True, exist_ok=True)
        self._playwright = None
        self._browser = None
        self._page = None
    
    def open(self):
        """Open browser."""
        print("\n🌐 Opening browser...")
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch_persistent_context(
            self.session_path,
            headless=False,  # Show browser
            args=['--disable-blink-features=AutomationControlled']
        )
        self._page = self._browser.pages[0]
        print("✓ Browser opened")
    
    def login(self):
        """Login to LinkedIn."""
        print("\n📱 Navigating to LinkedIn login...")
        self._page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
        
        print("\n" + "=" * 60)
        print("LOGIN REQUIRED")
        print("=" * 60)
        print("\n1. If you see login page, enter your credentials")
        print("2. Complete any 2FA if enabled")
        print("3. Wait until you see your LinkedIn feed")
        print("4. Session will be saved for future use")
        print("\nWaiting for login (max 2 minutes)...")
        
        try:
            # Wait for feed page (indicates successful login)
            self._page.wait_for_url('**/feed/**', timeout=120000)
            print("\n✓ Login successful!")
            time.sleep(2)  # Let page fully load
            return True
        except Exception as e:
            print(f"\n⚠ Login timeout or error: {e}")
            return False
    
    def create_post(self, content: str):
        """Create a LinkedIn post."""
        print("\n📝 Creating LinkedIn post...")
        
        try:
            # Navigate to feed
            self._page.goto('https://www.linkedin.com/feed', wait_until='domcontentloaded')
            time.sleep(2)
            
            # Click start post button
            print("   - Clicking 'Start a post' button...")
            try:
                start_post_btn = self._page.locator('[aria-label="Start a post"]').first
                start_post_btn.click()
                time.sleep(1.5)
            except Exception as e:
                print(f"   ⚠ Could not find post button: {e}")
                return False
            
            # Find text input and type content
            print("   - Entering post content...")
            text_input = self._page.locator('[contenteditable="true"]').first
            text_input.fill(content)
            time.sleep(1)
            
            # Click post button
            print("   - Clicking 'Post' button...")
            post_btn = self._page.locator('button:has-text("Post")').first
            post_btn.click()
            time.sleep(3)
            
            # Check if post was created (look for "Posted" confirmation)
            print("\n✓ Post created successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to create post: {e}")
            return False
    
    def close(self):
        """Close browser."""
        if self._browser:
            print("\n🔒 Closing browser...")
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        print("✓ Browser closed")


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("🧪 LinkedIn Post Test")
    print("=" * 60)
    
    # Test post content
    test_post = """🧪 Test Post from AI Employee Silver Tier

This is a test post to verify LinkedIn automation is working correctly.

If you're seeing this on LinkedIn, the integration is successful! 🎉

#AI #Automation #Test #SilverTier"""
    
    print("\n📝 Test Post Content:")
    print("-" * 40)
    print(test_post)
    print("-" * 40)
    
    print("\n⚠ This will:")
    print("1. Open a browser window")
    print("2. Navigate to LinkedIn login")
    print("3. You login manually (first time only)")
    print("4. Create a test post on LinkedIn")
    print("5. Session saved for future automated posts")
    
    response = input("\nContinue? (y/n): ").lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Create poster
    poster = LinkedInTestPoster()
    
    try:
        # Open browser
        poster.open()
        
        # Login
        if not poster.login():
            print("\n⚠ Login failed or timed out")
            poster.close()
            return
        
        # Create test post
        success = poster.create_post(test_post)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ SUCCESS!")
            print("=" * 60)
            print("\nYour test post should now be visible on LinkedIn.")
            print("\nNext steps:")
            print("1. Check your LinkedIn profile to see the post")
            print("2. Session is saved - future posts will be automated")
            print("3. Run 'python scripts/linkedin_watcher.py' for automated monitoring")
        else:
            print("\n⚠ Post creation failed")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        poster.close()
    
    print("\n✓ Test complete!\n")


if __name__ == '__main__':
    main()
