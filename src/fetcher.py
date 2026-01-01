"""RSS Feed Fetcher for Bitcoin news"""

import feedparser
from datetime import datetime
from typing import Iterator
from dataclasses import dataclass
from dateutil import parser as date_parser
import httpx


@dataclass
class Article:
    """Represents a fetched article."""
    url: str
    title: str
    summary: str
    source: str
    published_at: str | None


def fetch_feed(feed_url: str, timeout: int = 30) -> list[Article]:
    """Fetch and parse a single RSS feed."""
    articles = []

    try:
        # Some feeds need a browser user-agent
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; BitcoinContentCurator/1.0)"
        }
        response = httpx.get(feed_url, headers=headers, timeout=timeout, follow_redirects=True)
        feed = feedparser.parse(response.text)

        source_name = feed.feed.get("title", feed_url)

        for entry in feed.entries:
            url = entry.get("link", "")
            if not url:
                continue

            title = entry.get("title", "Untitled")

            # Get summary/description
            summary = ""
            if "summary" in entry:
                summary = entry.summary
            elif "description" in entry:
                summary = entry.description
            elif "content" in entry and entry.content:
                summary = entry.content[0].get("value", "")

            # Clean up HTML from summary
            summary = _strip_html(summary)[:1000]  # Truncate long summaries

            # Parse published date
            published_at = None
            if "published" in entry:
                try:
                    published_at = date_parser.parse(entry.published).isoformat()
                except (ValueError, TypeError):
                    pass
            elif "updated" in entry:
                try:
                    published_at = date_parser.parse(entry.updated).isoformat()
                except (ValueError, TypeError):
                    pass

            articles.append(Article(
                url=url,
                title=title,
                summary=summary,
                source=source_name,
                published_at=published_at
            ))

    except Exception as e:
        print(f"Error fetching {feed_url}: {e}")

    return articles


def fetch_all_feeds(feed_urls: list[str]) -> Iterator[Article]:
    """Fetch all configured RSS feeds, yield articles."""
    seen_urls = set()

    for feed_url in feed_urls:
        print(f"Fetching: {feed_url}")
        articles = fetch_feed(feed_url)

        for article in articles:
            # Dedupe within this run
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                yield article


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    import re
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    # Decode common HTML entities
    clean = clean.replace('&amp;', '&')
    clean = clean.replace('&lt;', '<')
    clean = clean.replace('&gt;', '>')
    clean = clean.replace('&quot;', '"')
    clean = clean.replace('&#39;', "'")
    clean = clean.replace('&nbsp;', ' ')
    return clean
