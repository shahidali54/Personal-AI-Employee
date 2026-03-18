#!/usr/bin/env python3
"""
Run All Watchers - Start all watchers for the AI Employee.

This script starts:
- File System Watcher
- Gmail Watcher
- WhatsApp Watcher (optional)
- LinkedIn Watcher (optional)

Usage:
    python scripts/run_all_watchers.py ./AI_Employee_Vault

Or run individual watchers:
    python scripts/gmail_watcher.py ./AI_Employee_Vault
    python scripts/filesystem_watcher.py ./AI_Employee_Vault
"""

import os
import sys
import time
import signal
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default vault path from environment
DEFAULT_VAULT_PATH = os.getenv('VAULT_PATH', './AI_Employee_Vault')

# Watcher configurations
WATCHERS = {
    'filesystem': {
        'script': 'filesystem_watcher.py',
        'interval': 30,
        'enabled': True,
        'description': 'File System Watcher',
    },
    'gmail': {
        'script': 'gmail_watcher.py',
        'interval': 120,
        'enabled': True,
        'description': 'Gmail Watcher',
        'requires_auth': True,
    },
    'whatsapp': {
        'script': 'whatsapp_watcher.py',
        'interval': 30,
        'enabled': False,  # Disabled by default
        'description': 'WhatsApp Watcher',
        'requires_auth': True,
    },
    'linkedin': {
        'script': 'linkedin_watcher.py',
        'interval': 300,
        'enabled': False,  # Disabled by default
        'description': 'LinkedIn Watcher',
        'requires_auth': True,
    },
}


class WatcherRunner:
    """Manages multiple watcher processes."""
    
    def __init__(self, vault_path: str, enable_watchers: list = None):
        """
        Initialize watcher runner.
        
        Args:
            vault_path: Path to Obsidian vault
            enable_watchers: List of watcher names to enable
        """
        self.vault_path = Path(vault_path).absolute()
        self.scripts_dir = Path(__file__).parent
        self.processes = {}
        self.running = True
        
        # Enable specified watchers
        if enable_watchers:
            for name in WATCHERS:
                WATCHERS[name]['enabled'] = name in enable_watchers
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n\n⚠ Received signal {signum}, shutting down...")
        self.running = False
    
    def check_auth(self, watcher_name: str) -> bool:
        """Check if watcher has required authentication."""
        if watcher_name == 'gmail':
            # Check for token.json
            token_paths = [
                Path('token.json'),
                self.scripts_dir / 'token.json',
            ]
            for path in token_paths:
                if path.exists():
                    return True
            print(f"\n⚠ Gmail authentication required!")
            print(f"   Run: python scripts/gmail_auth.py")
            return False
        
        # Add other auth checks as needed
        return True
    
    def start_watcher(self, name: str, config: dict):
        """Start a watcher process."""
        script = config['script']
        script_path = self.scripts_dir / script
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return None
        
        # Check auth if required
        if config.get('requires_auth') and not self.check_auth(name):
            print(f"⚠ Skipping {config['description']} - authentication required")
            return None
        
        # Start process
        cmd = [sys.executable, str(script_path), str(self.vault_path)]
        print(f"\n📌 Starting {config['description']}...")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Interval: {config['interval']}s")
        
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Start output thread
            threading.Thread(
                target=self._stream_output,
                args=(proc, name),
                daemon=True
            ).start()
            
            return proc
            
        except Exception as e:
            print(f"❌ Failed to start {config['description']}: {e}")
            return None
    
    def _stream_output(self, proc, name):
        """Stream process output to console."""
        prefix = f"[{name}] "
        for line in proc.stdout:
            if self.running:
                print(f"{prefix}{line.strip()}")
    
    def run(self):
        """Run all enabled watchers."""
        print("\n" + "=" * 60)
        print("🤖 AI Employee - Watcher Suite")
        print("=" * 60)
        print(f"\nVault: {self.vault_path}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nEnabled Watchers:")
        
        enabled_count = 0
        for name, config in WATCHERS.items():
            if config['enabled']:
                status = "✓" if not config.get('requires_auth') else "⚠"
                print(f"  {status} {config['description']} ({config['interval']}s)")
                enabled_count += 1
        
        if enabled_count == 0:
            print("\n⚠ No watchers enabled!")
            print("Enable with: python scripts/run_all_watchers.py --enable gmail,filesystem")
            return
        
        print("\n" + "=" * 60)
        print("Press Ctrl+C to stop all watchers")
        print("=" * 60)
        
        # Start watchers
        for name, config in WATCHERS.items():
            if config['enabled']:
                proc = self.start_watcher(name, config)
                if proc:
                    self.processes[name] = proc
        
        print("\n✓ All watchers started successfully!")
        print("\nMonitoring for new items...\n")
        
        # Monitor processes
        try:
            while self.running:
                time.sleep(1)
                
                # Check if any process died
                for name, proc in list(self.processes.items()):
                    if proc.poll() is not None:
                        print(f"\n⚠ {WATCHERS[name]['description']} exited, restarting...")
                        new_proc = self.start_watcher(name, WATCHERS[name])
                        if new_proc:
                            self.processes[name] = new_proc
                        else:
                            del self.processes[name]
        
        except KeyboardInterrupt:
            pass
        
        # Cleanup
        print("\n\nStopping all watchers...")
        for name, proc in self.processes.items():
            proc.terminate()
            proc.wait(timeout=5)
        
        print("✓ All watchers stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run all AI Employee watchers'
    )
    parser.add_argument(
        'vault_path',
        nargs='?',
        default=DEFAULT_VAULT_PATH,
        help=f'Path to Obsidian vault (default: {DEFAULT_VAULT_PATH})'
    )
    parser.add_argument(
        '--enable',
        type=str,
        default=None,
        help='Comma-separated list of watchers to enable (e.g., gmail,filesystem)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available watchers'
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("\nAvailable Watchers:")
        print("-" * 40)
        for name, config in WATCHERS.items():
            status = "Enabled" if config['enabled'] else "Disabled"
            auth = " (requires auth)" if config.get('requires_auth') else ""
            print(f"  {name}: {config['description']}{auth} - {status}")
        return
    
    # Parse enabled watchers
    enable_list = None
    if args.enable:
        enable_list = [w.strip() for w in args.enable.split(',')]
    
    # Run watchers
    runner = WatcherRunner(args.vault_path, enable_list)
    runner.run()


if __name__ == '__main__':
    main()
