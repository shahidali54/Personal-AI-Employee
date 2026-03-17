#!/usr/bin/env python3
"""
Test script to verify the FileSystemWatcher works correctly.

Usage:
    python test_watcher.py

This script:
1. Creates a test file in the Inbox folder
2. Runs the watcher for one cycle
3. Verifies the action file was created in Needs_Action
"""

import time
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from filesystem_watcher import FileSystemWatcher, FileDropItem


def test_watcher():
    """Test the file system watcher."""
    vault_path = Path('./AI_Employee_Vault').absolute()
    print(f"Testing watcher with vault: {vault_path}")
    
    # Create watcher
    watcher = FileSystemWatcher(str(vault_path), check_interval=1)
    
    # Create a test file in Inbox
    inbox = vault_path / 'Inbox'
    inbox.mkdir(parents=True, exist_ok=True)
    
    test_file = inbox / 'test_document.txt'
    test_file.write_text("This is a test file for the AI Employee watcher.")
    print(f"Created test file: {test_file}")
    
    # Run one check cycle
    print("Running watcher check...")
    items = watcher.check_for_updates()
    print(f"Found {len(items)} new item(s)")
    
    if items:
        for item in items:
            filepath = watcher.create_action_file(item)
            if filepath:
                print(f"✓ Created action file: {filepath.name}")
                
                # Verify file exists
                if filepath.exists():
                    print(f"✓ Action file verified")
                    
                    # Read and display content
                    content = filepath.read_text()
                    print(f"\n--- Action File Content ---\n")
                    print(content[:500] + "..." if len(content) > 500 else content)
                    print(f"\n--- End Content ---\n")
                else:
                    print(f"✗ Action file not found!")
            else:
                print(f"✗ Failed to create action file")
    else:
        print("No items found (may have been processed before)")
    
    # Check if test file was moved
    files_folder = vault_path / 'Files'
    if files_folder.exists():
        copied_files = list(files_folder.glob('test_document*'))
        if copied_files:
            print(f"✓ File was copied to Files folder: {copied_files[0].name}")
        else:
            print("✗ File was not copied to Files folder")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_watcher()
