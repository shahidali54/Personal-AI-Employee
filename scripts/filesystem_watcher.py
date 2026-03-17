#!/usr/bin/env python3
"""
File System Watcher - Monitors the Inbox folder for new files.

This watcher is ideal for Bronze Tier as it:
- Requires no external API setup
- Works immediately with drag-and-drop
- Demonstrates the core watcher pattern

When a file is dropped into /Inbox, this watcher:
1. Detects the new file
2. Creates a metadata .md file in /Needs_Action
3. Copies the original file for processing
"""

import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from base_watcher import BaseWatcher


class FileDropItem:
    """Represents a file dropped into the Inbox."""
    
    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.name = source_path.name
        self.size = source_path.stat().st_size
        self.modified = datetime.fromtimestamp(source_path.stat().st_mtime)
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate MD5 hash for deduplication."""
        hash_md5 = hashlib.md5()
        with open(self.source_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'size': self.size,
            'modified': self.modified.isoformat(),
            'hash': self.hash,
            'source_path': str(self.source_path)
        }


class FileSystemWatcher(BaseWatcher):
    """
    Watches the Inbox folder for new files.
    
    Files dropped into /Inbox trigger creation of action files in /Needs_Action.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 30 for files)
        """
        super().__init__(vault_path, check_interval)
        self.drop_folder = self.inbox  # Files dropped in Inbox
        self.files_folder = self.vault_path / 'Files'  # Store processed files here
        self.files_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed file hashes to avoid duplicates
        self.processed_hashes: set = set()
        
        # Load previously processed files from log
        self._load_processed_log()
    
    def _load_processed_log(self):
        """Load list of processed file hashes from log."""
        log_file = self.vault_path / 'Logs' / 'processed_files.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                self.processed_hashes = set(line.strip() for line in f if line.strip())
    
    def _save_to_log(self, file_hash: str):
        """Save processed file hash to log."""
        log_file = self.vault_path / 'Logs' / 'processed_files.log'
        with open(log_file, 'a') as f:
            f.write(f"{file_hash}\n")
    
    def check_for_updates(self) -> List[FileDropItem]:
        """
        Check for new files in the Inbox folder.
        
        Returns:
            List of FileDropItem objects for new files
        """
        new_items = []
        
        if not self.drop_folder.exists():
            return new_items
        
        # Check all files in inbox (excluding already processed .log files)
        for file_path in self.drop_folder.iterdir():
            if file_path.is_file() and not file_path.name.endswith('.log'):
                item = FileDropItem(file_path)
                
                # Skip if already processed
                if item.hash in self.processed_hashes:
                    continue
                
                new_items.append(item)
        
        return new_items
    
    def create_action_file(self, item: FileDropItem) -> Optional[Path]:
        """
        Create an action file for the dropped file.
        
        Args:
            item: FileDropItem to process
            
        Returns:
            Path to created action file
        """
        # Copy file to Files folder
        dest_path = self.files_folder / item.name
        
        # Handle duplicate filenames
        counter = 1
        while dest_path.exists():
            stem = Path(item.name).stem
            suffix = Path(item.name).suffix
            dest_path = self.files_folder / f"{stem}_{counter}{suffix}"
            counter += 1
        
        try:
            shutil.copy2(item.source_path, dest_path)
        except Exception as e:
            self.logger.error(f'Failed to copy file: {e}')
            return None
        
        # Remove original from inbox
        try:
            item.source_path.unlink()
        except Exception as e:
            self.logger.warning(f'Failed to remove original file: {e}')
        
        # Create action file
        filename = self.generate_filename('FILE', Path(item.name).stem)
        filepath = self.needs_action / filename
        
        # Determine file type based on extension
        file_type = self._guess_type(item.name)
        
        content = f"""{self.create_frontmatter(
            item_type='file_drop',
            original_name=f'"{item.name}"',
            file_path=f'"{dest_path.relative_to(self.vault_path)}"',
            file_size=str(item.size),
            file_hash=f'"{item.hash}"'
        )}

## File Dropped for Processing

**Original Name:** {item.name}
**Size:** {self._format_size(item.size)}
**Location:** `/{dest_path.relative_to(self.vault_path)}`

## Suggested Actions

- [ ] Review file contents
- [ ] Categorize file type
- [ ] Take appropriate action
- [ ] Move to Done when complete

## Notes

```
Add notes about this file here
```

---
*Detected by FileSystemWatcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        filepath.write_text(content)
        
        # Log as processed
        self.processed_hashes.add(item.hash)
        self._save_to_log(item.hash)
        
        return filepath
    
    def _guess_type(self, filename: str) -> str:
        """Guess the file type/category based on extension."""
        ext = Path(filename).suffix.lower()
        
        type_map = {
            '.pdf': 'document',
            '.doc': 'document',
            '.docx': 'document',
            '.txt': 'document',
            '.md': 'document',
            '.xls': 'spreadsheet',
            '.xlsx': 'spreadsheet',
            '.csv': 'spreadsheet',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.mp4': 'video',
            '.mov': 'video',
            '.zip': 'archive',
            '.rar': 'archive',
            '.7z': 'archive',
        }
        
        return type_map.get(ext, 'unknown')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


def main():
    """Run the file system watcher."""
    import sys
    
    # Default vault path
    vault_path = './AI_Employee_Vault'
    
    # Allow override from command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    
    # Check interval in seconds (30 for files)
    check_interval = 30
    
    watcher = FileSystemWatcher(vault_path, check_interval)
    watcher.run()


if __name__ == '__main__':
    main()
