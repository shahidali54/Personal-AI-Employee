#!/usr/bin/env python3
"""
LinkedIn MCP Server - LinkedIn automation for posting and engagement.

This server provides LinkedIn capabilities to Qwen Code via MCP protocol.
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
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

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LinkedInMCP')


class LinkedInClient:
    """LinkedIn automation client using Playwright."""
    
    def __init__(self, session_path: str = None):
        """Initialize LinkedIn client."""
        self.session_path = Path(session_path or os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
        self.session_path.mkdir(parents=True, exist_ok=True)
        self._playwright = None
        self._browser = None
        self._page = None
        self._init_browser()
    
    def _init_browser(self):
        """Initialize browser with persistent context."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch_persistent_context(
            self.session_path,
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        self._page = self._browser.pages[0]
        logger.info("LinkedIn browser initialized")
    
    def _ensure_logged_in(self) -> bool:
        """Ensure logged in to LinkedIn."""
        self._page.goto('https://www.linkedin.com/feed', wait_until='domcontentloaded')
        
        try:
            # Check for feed (indicates logged in)
            self._page.wait_for_selector('[data-testid="update-component"]', timeout=5000)
            return True
        except PlaywrightTimeout:
            logger.warning("Not logged in. Authentication required.")
            return False
    
    def post(self, content: str, image_path: str = None) -> dict:
        """Create a LinkedIn post."""
        try:
            if not self._ensure_logged_in():
                return {'success': False, 'error': 'Not logged in'}
            
            # Click on post creation box
            try:
                start_post_btn = self._page.locator('[aria-label="Start a post"]')
                start_post_btn.click()
                time.sleep(1)
            except:
                logger.warning("Could not find post button, trying alternative method")
            
            # Find text input and type content
            text_input = self._page.locator('[contenteditable="true"][aria-label*="post"], div[contenteditable="true"]').first
            text_input.fill(content)
            time.sleep(0.5)
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                try:
                    # Click media icon
                    media_btn = self._page.locator('[aria-label*="photo"], [aria-label*="image"]').first
                    media_btn.click()
                    time.sleep(0.5)
                    
                    # Upload file
                    file_input = self._page.locator('input[type="file"]').first
                    file_input.set_input_files(image_path)
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"Could not attach image: {e}")
            
            # Click post button
            post_btn = self._page.locator('button:has-text("Post"), button:has-text("post")').first
            post_btn.click()
            time.sleep(2)
            
            logger.info("LinkedIn post created successfully")
            return {'success': True, 'posted_at': datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"Failed to create post: {e}")
            return {'success': False, 'error': str(e)}
    
    def schedule_post(self, content: str, publish_time: str, image_path: str = None) -> dict:
        """Schedule a post for future publishing."""
        # For now, save to file for scheduler to process
        schedule_file = self.session_path / f'scheduled_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        schedule_data = {
            'content': content,
            'publish_time': publish_time,
            'image_path': image_path,
            'created_at': datetime.now().isoformat(),
            'status': 'scheduled'
        }
        
        with open(schedule_file, 'w') as f:
            json.dump(schedule_data, f, indent=2)
        
        logger.info(f"Scheduled post saved to {schedule_file}")
        return {'success': True, 'scheduled_file': str(schedule_file)}
    
    def engage(self, action: str = 'like', comment_text: str = None) -> dict:
        """Engage with posts in feed."""
        try:
            if not self._ensure_logged_in():
                return {'success': False, 'error': 'Not logged in'}
            
            # Find first post in feed
            posts = self._page.locator('[data-testid="update-component"]').all()
            
            if not posts:
                return {'success': False, 'error': 'No posts found'}
            
            post = posts[0]
            
            if action == 'like':
                like_btn = post.locator('button:has-text("Like"), button:has-text("like")').first
                like_btn.click()
                logger.info("Liked post")
                return {'success': True, 'action': 'like'}
            
            elif action == 'comment' and comment_text:
                comment_btn = post.locator('button:has-text("Comment"), button:has-text("comment")').first
                comment_btn.click()
                time.sleep(0.5)
                
                comment_input = self._page.locator('[contenteditable="true"][aria-label*="comment"]').first
                comment_input.fill(comment_text)
                time.sleep(0.5)
                
                post_comment_btn = self._page.locator('button:has-text("Comment"), button:has-text("comment")').last
                post_comment_btn.click()
                logger.info("Commented on post")
                return {'success': True, 'action': 'comment'}
            
            return {'success': False, 'error': 'Invalid action'}
            
        except Exception as e:
            logger.error(f"Failed to engage: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_analytics(self, days: int = 7) -> dict:
        """Get post analytics."""
        # Simplified analytics - just return recent activity
        return {
            'period_days': days,
            'posts': 0,
            'impressions': 0,
            'engagement': 0,
            'note': 'Full analytics requires LinkedIn API access'
        }
    
    def close(self):
        """Close browser."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()


class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP protocol."""
    
    linkedin = None
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
            method = request.get('method', '')
            params = request.get('params', {})
            
            if method == 'tools/call':
                result = self.handle_tool_call(params)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'result': result}).encode())
            elif method == 'tools/list':
                tools = self.list_tools()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'tools': tools}).encode())
            else:
                self.send_error(404, 'Method not found')
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_error(500, str(e))
    
    def handle_tool_call(self, params: dict) -> dict:
        """Handle tool call."""
        tool_name = params.get('name', '')
        arguments = params.get('arguments', {})
        
        logger.info(f"Tool call: {tool_name}")
        
        if tool_name == 'linkedin_post':
            return self.linkedin.post(
                content=arguments.get('content', ''),
                image_path=arguments.get('image_path')
            )
        elif tool_name == 'linkedin_schedule_post':
            return self.linkedin.schedule_post(
                content=arguments.get('content', ''),
                publish_time=arguments.get('publish_time', ''),
                image_path=arguments.get('image_path')
            )
        elif tool_name == 'linkedin_engage':
            return self.linkedin.engage(
                action=arguments.get('action', 'like'),
                comment_text=arguments.get('comment_text')
            )
        elif tool_name == 'linkedin_post_analytics':
            return self.linkedin.get_analytics(
                days=arguments.get('days', 7)
            )
        else:
            return {'error': f'Unknown tool: {tool_name}'}
    
    def list_tools(self) -> list:
        """List available tools."""
        return [
            {
                'name': 'linkedin_post',
                'description': 'Create a LinkedIn post',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'content': {'type': 'string', 'description': 'Post content'},
                        'image_path': {'type': 'string', 'description': 'Image path'}
                    },
                    'required': ['content']
                }
            },
            {
                'name': 'linkedin_schedule_post',
                'description': 'Schedule a LinkedIn post',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'content': {'type': 'string', 'description': 'Post content'},
                        'publish_time': {'type': 'string', 'description': 'ISO datetime'},
                        'image_path': {'type': 'string', 'description': 'Image path'}
                    },
                    'required': ['content', 'publish_time']
                }
            },
            {
                'name': 'linkedin_engage',
                'description': 'Engage with LinkedIn posts',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'action': {'type': 'string', 'enum': ['like', 'comment']},
                        'comment_text': {'type': 'string', 'description': 'Comment text'}
                    },
                    'required': ['action']
                }
            },
            {
                'name': 'linkedin_post_analytics',
                'description': 'Get post analytics',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'days': {'type': 'integer', 'description': 'Days to analyze'}
                    }
                }
            }
        ]
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Start LinkedIn MCP Server."""
    port = int(os.getenv('LINKEDIN_MCP_PORT', 8810))

    # Initialize LinkedIn client
    logger.info("Initializing LinkedIn client...")
    try:
        linkedin = LinkedInClient()
        MCPRequestHandler.linkedin = linkedin
        logger.info("LinkedIn client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LinkedIn: {e}")
        sys.exit(1)

    # Start server
    server = HTTPServer(('localhost', port), MCPRequestHandler)
    logger.info(f"LinkedIn MCP Server running on http://localhost:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.shutdown()
        MCPRequestHandler.linkedin.close()


if __name__ == '__main__':
    main()
