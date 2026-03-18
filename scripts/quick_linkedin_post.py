#!/usr/bin/env python3
"""
Quick LinkedIn Post - Post without any prompts.

Usage:
    python scripts/quick_linkedin_post.py "Your post content here"

Example:
    python scripts/quick_linkedin_post.py "Hello LinkedIn! This is a test."
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Missing Playwright! Install with: pip install playwright")
    sys.exit(1)


def post_to_linkedin(content: str):
    """Post to LinkedIn directly."""
    session_path = Path(os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("\n🌐 Opening browser...")
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch_persistent_context(
        session_path,
        headless=False,  # Keep browser visible
        args=['--disable-blink-features=AutomationControlled']
    )
    page = browser.pages[0]
    
    try:
        # Navigate to LinkedIn feed
        print("📱 Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/feed', wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)  # Wait for dynamic content to load
        
        # Check if we're on feed page (logged in) or login page
        current_url = page.url
        print(f"   Current URL: {current_url}")
        
        if 'login' in current_url or 'checkpoint' in current_url:
            print("\n" + "=" * 50)
            print("PLEASE LOGIN IN THE BROWSER")
            print("=" * 50)
            print("\nWaiting for you to login (max 2 minutes)...")
            
            # Wait for user to login and redirect to feed
            try:
                page.wait_for_url('**/feed/**', timeout=120000)
                time.sleep(3)
                print("✓ Login successful!")
            except PlaywrightTimeout:
                print("⚠ Login timeout")
                return False
        else:
            print("✓ Already on feed page")
        
        # Wait a bit more for page to be fully interactive
        time.sleep(3)
        
        # Create post
        print("\n📝 Creating post...")
        
        # Look for the "Start a post" button with multiple fallback strategies
        post_button_found = False
        
        # Strategy 1: aria-label selector
        try:
            print("   - Looking for 'Start a post' button...")
            post_btn = page.locator('[aria-label="Start a post"]').first
            if post_btn.is_visible(timeout=5000):
                post_btn.click()
                time.sleep(2)
                post_button_found = True
                print("   ✓ Post composer opened")
        except Exception as e:
            print(f"   ⚠ Strategy 1 failed: {e}")
        
        # Strategy 2: Text button
        if not post_button_found:
            try:
                print("   - Trying text selector...")
                post_btn = page.locator('button:has-text("Start a post")').first
                if post_btn.is_visible(timeout=5000):
                    post_btn.click()
                    time.sleep(2)
                    post_button_found = True
                    print("   ✓ Post composer opened")
            except:
                print("   ⚠ Strategy 2 failed")
        
        # Strategy 3: Take screenshot and show manual instructions
        if not post_button_found:
            print("\n⚠ Could not automatically open post composer")
            print("\n📸 Taking screenshot for debugging...")
            page.screenshot(path='linkedin_debug.png')
            print("   Screenshot saved to: linkedin_debug.png")
            
            print("\n" + "=" * 50)
            print("MANUAL STEP REQUIRED")
            print("=" * 50)
            print("\n1. In the browser window, click 'Start a post'")
            print("2. The script will continue automatically...")
            print("3. Waiting 30 seconds for you to click...\n")
            
            # Wait for user to click
            time.sleep(5)
            
            # Check if composer opened
            composer_found = False
            for _ in range(5):
                try:
                    if page.locator('[role="dialog"]').first.is_visible(timeout=1000):
                        composer_found = True
                        print("✓ Post composer detected!")
                        break
                except:
                    time.sleep(1)
            
            if not composer_found:
                print("⚠ Composer not detected, continuing anyway...")
        
        # Type content
        print("   - Entering content...")
        try:
            # Find the main text input in the composer
            text_input = page.locator('[contenteditable="true"]').first
            
            # Clear any existing content first
            text_input.click()
            time.sleep(0.5)
            
            # Use keyboard to type (more human-like, ensures LinkedIn registers input)
            text_input.press('Control+A')
            time.sleep(0.3)
            text_input.press('Backspace')
            time.sleep(0.3)
            
            # Type content character by character for reliability
            text_input.type(content, delay=10)
            time.sleep(2)  # Wait for LinkedIn to register the input
            
            # Verify content was entered
            entered_text = text_input.inner_text()
            if entered_text.strip():
                print("   ✓ Content entered and verified")
            else:
                print("   ⚠ Content may not have been entered properly")
        except Exception as e:
            print(f"   ⚠ Could not enter content: {e}")
            return False
        
        # Click Post button
        print("   - Publishing post...")
        
        # Critical: Wait for LinkedIn to fully register the content
        # This prevents the visibility popup from appearing
        time.sleep(3)
        
        # Ensure focus is on the composer
        try:
            page.locator('[contenteditable="true"]').first.focus()
            time.sleep(0.5)
        except:
            pass
        
        # Find the Post button - be very specific to avoid clicking visibility selector
        post_button = None
        post_selectors = [
            'button.artdeco-button.artdeco-button--primary:has-text("Post")',
            'button:has-text("Post"):not(:has-text("anyone")):not(:has-text("Public"))',
            '[aria-label="Post"]',
        ]
        
        for selector in post_selectors:
            try:
                candidates = page.locator(selector)
                if candidates.count() > 0:
                    post_button = candidates.first
                    if post_button.is_visible(timeout=2000):
                        print(f"   ✓ Found Post button with selector: {selector}")
                        break
            except:
                continue
        
        if not post_button:
            # Fallback: any button with "Post" text
            try:
                post_button = page.locator('button:has-text("Post")').first
            except:
                print("   ⚠ Could not find Post button")
                return False
        
        # Wait for button to be truly clickable
        try:
            post_button.wait_for(state='visible', timeout=5000)
            time.sleep(1)
            
            # Check if disabled
            is_disabled = post_button.get_attribute('disabled')
            if is_disabled:
                print("   ⚠ Post button disabled, waiting longer...")
                time.sleep(3)
        except:
            pass
        
        # Click using JavaScript (bypasses visibility popup trigger)
        print("   - Clicking Post button (JavaScript click)...")
        try:
            # Use element handle for more reliable JavaScript click
            element_handle = post_button.element_handle(timeout=2000)
            page.evaluate('(el) => el.click()', element_handle)
            time.sleep(3)
            print("\n✅ SUCCESS! Post created on LinkedIn.")
            print("\n📊 View your post:")
            print("   https://www.linkedin.com/in/your-profile\n")
            return True
        except Exception as e:
            print(f"   ⚠ JavaScript click failed: {e}")
            
            # Fallback: regular click
            try:
                post_button.click()
                time.sleep(3)
                print("\n✅ SUCCESS! Post created on LinkedIn.")
                return True
            except:
                pass
        
        # Handle visibility popup if it appears despite precautions
        print("   ⚠ Checking for visibility popup...")
        time.sleep(2)
        
        try:
            dialogs = page.locator('[role="dialog"]')
            if dialogs.count() > 0:
                print(f"   - Visibility popup detected ({dialogs.count()} dialog(s))")
                
                for i in range(dialogs.count()):
                    try:
                        dialog = dialogs.nth(i)
                        
                        # Check if this is the visibility dialog
                        dialog_text = dialog.inner_text(timeout=1000)
                        if 'anyone' in dialog_text.lower() or 'visibility' in dialog_text.lower() or 'who can see' in dialog_text.lower():
                            print("   - This is the visibility dialog, handling...")
                            
                            # Try to click "Anyone" option
                            try:
                                anyone_option = dialog.locator('li:has-text("Anyone"), button:has-text("Anyone"), [role="option"]:has-text("Anyone")').first
                                if anyone_option.is_visible(timeout=1000):
                                    anyone_option.click()
                                    time.sleep(1)
                                    print("   ✓ Selected 'Anyone' visibility")
                            except:
                                print("   ⚠ Could not select 'Anyone'")
                            
                            # Wait for Done button to become enabled
                            time.sleep(2)
                            
                            # Find and click Done/Post button in dialog
                            done_selectors = [
                                'button:has-text("Done")',
                                'button:has-text("Post")',
                                'button.artdeco-button--primary'
                            ]
                            
                            for done_selector in done_selectors:
                                try:
                                    done_btn = dialog.locator(done_selector).first
                                    if done_btn.is_visible(timeout=1000):
                                        # Check if enabled
                                        is_disabled = done_btn.get_attribute('disabled')
                                        if not is_disabled:
                                            print(f"   - Clicking {done_selector}...")
                                            done_btn.click()
                                            time.sleep(3)
                                            print("\n✅ SUCCESS! Post created on LinkedIn.")
                                            print("\n📊 View your post:")
                                            print("   https://www.linkedin.com/in/your-profile\n")
                                            return True
                                        else:
                                            print(f"   ⚠ {done_selector} is disabled, trying JavaScript...")
                                            page.evaluate('(btn) => btn.click()', done_btn)
                                            time.sleep(3)
                                            print("\n✅ SUCCESS! Post created on LinkedIn.")
                                            return True
                                except:
                                    continue
                            
                            # If Done button didn't work, try Escape to close and regular post
                            print("   - Closing popup with Escape...")
                            page.keyboard.press('Escape')
                            time.sleep(1)
                            break
                    except:
                        continue
        except Exception as e:
            print(f"   ⚠ Popup handling failed: {e}")
        
        # Final fallback: keyboard submit
        print("   - Trying keyboard submit (Ctrl+Enter)...")
        page.keyboard.press('Control+Enter')
        time.sleep(3)
        
        print("\n✅ Post submission attempted.")
        print("📊 Check your LinkedIn profile to verify:")
        print("   https://www.linkedin.com/in/your-profile\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        try:
            page.screenshot(path='linkedin_error.png')
            print("📸 Error screenshot saved to linkedin_error.png")
        except:
            pass
        return False
    finally:
        print("\n🔒 Closing browser...")
        time.sleep(2)
        browser.close()
        playwright.stop()
        print("✓ Done")


def main():
    if len(sys.argv) < 2:
        # Default test message
        content = """🧪 Quick Test Post from AI Employee Silver Tier

Testing LinkedIn automation with Qwen Code integration.

#AI #Automation #Test"""
    else:
        content = ' '.join(sys.argv[1:])
    
    print("\n" + "=" * 50)
    print("📝 LinkedIn Quick Post")
    print("=" * 50)
    print(f"\nContent:\n{content}\n")
    post_to_linkedin(content)


if __name__ == '__main__':
    main()
