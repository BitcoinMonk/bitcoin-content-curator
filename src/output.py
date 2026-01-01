"""Output module for writing content to Silver Bullet (markdown files)"""

from datetime import datetime
from pathlib import Path
from typing import Optional


class SilverBulletOutput:
    """Writes content to Silver Bullet space as markdown files."""

    def __init__(self, space_path: Path):
        """
        Initialize with path to Silver Bullet space.

        Args:
            space_path: Path to the Silver Bullet space directory (e.g., ~/data/notes)
        """
        self.space_path = Path(space_path).expanduser()
        self._ensure_structure()

    def _ensure_structure(self) -> None:
        """Create content directory structure if needed."""
        content_dir = self.space_path / "Content"
        content_dir.mkdir(parents=True, exist_ok=True)

    def _read_existing(self, filepath: Path) -> str:
        """Read existing file content or return empty string."""
        if filepath.exists():
            return filepath.read_text()
        return ""

    def append_content(
        self,
        category: str,
        title: str,
        url: str,
        source: str,
        score: float,
        score_reason: str,
        tweet: Optional[str] = None,
        thread: Optional[str] = None,
        linkedin: Optional[str] = None,
        prepend: bool = True
    ) -> None:
        """
        Append content to the appropriate markdown file.

        Args:
            category: 'ready', 'review', or 'archive'
            title: Article title
            url: Article URL
            source: Source name
            score: Article score
            score_reason: Why it got this score
            tweet: Generated tweet
            thread: Generated thread
            linkedin: Generated LinkedIn post
            prepend: If True, add to top of file; otherwise append
        """
        filename_map = {
            "ready": "Content/ReadyToPost.md",
            "review": "Content/NeedsReview.md",
            "archive": "Content/Archive.md"
        }

        filepath = self.space_path / filename_map.get(category, "Content/Other.md")
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Build the entry
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = self._format_entry(
            title=title,
            url=url,
            source=source,
            score=score,
            score_reason=score_reason,
            timestamp=now,
            tweet=tweet,
            thread=thread,
            linkedin=linkedin
        )

        # Read existing content
        existing = self._read_existing(filepath)

        # Add header if file is new
        if not existing:
            header = self._get_header(category)
            existing = header

        # Prepend or append
        if prepend:
            # Find where content starts (after header)
            lines = existing.split("\n")
            header_end = 0
            for i, line in enumerate(lines):
                if line.startswith("---") and i > 0:
                    header_end = i + 1
                    break

            header_part = "\n".join(lines[:header_end])
            content_part = "\n".join(lines[header_end:])

            new_content = f"{header_part}\n{entry}\n{content_part}"
        else:
            new_content = f"{existing}\n{entry}"

        filepath.write_text(new_content.strip() + "\n")

    def _get_header(self, category: str) -> str:
        """Get markdown header for category file."""
        titles = {
            "ready": "Ready to Post",
            "review": "Needs Review",
            "archive": "Archive"
        }
        return f"""---
title: {titles.get(category, 'Content')}
tags: #content #bitcoin
---

"""

    def _format_entry(
        self,
        title: str,
        url: str,
        source: str,
        score: float,
        score_reason: str,
        timestamp: str,
        tweet: Optional[str] = None,
        thread: Optional[str] = None,
        linkedin: Optional[str] = None
    ) -> str:
        """Format a single content entry as markdown."""
        entry = f"""
## {title}

**Source:** {source} | **Score:** {score}/10 | **Added:** {timestamp}
**Link:** {url}
**Why:** {score_reason}
"""

        if tweet:
            entry += f"""
### Tweet
```
{tweet}
```
"""

        if thread:
            entry += f"""
### Thread
```
{thread}
```
"""

        if linkedin:
            entry += f"""
### LinkedIn
{linkedin}
"""

        entry += "\n---\n"
        return entry


def write_to_silverbullet(
    space_path: str,
    category: str,
    title: str,
    url: str,
    source: str,
    score: float,
    score_reason: str,
    tweet: Optional[str] = None,
    thread: Optional[str] = None,
    linkedin: Optional[str] = None
) -> None:
    """Convenience function to write content to Silver Bullet."""
    output = SilverBulletOutput(space_path)
    output.append_content(
        category=category,
        title=title,
        url=url,
        source=source,
        score=score,
        score_reason=score_reason,
        tweet=tweet,
        thread=thread,
        linkedin=linkedin
    )
