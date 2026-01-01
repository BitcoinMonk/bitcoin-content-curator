"""Configuration for Bitcoin Content Curator"""

import os
from pathlib import Path

# API Keys
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# RSS Feeds - Bitcoin focused
RSS_FEEDS = [
    "https://bitcoinmagazine.com/.rss/full/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://cointelegraph.com/rss/tag/bitcoin",
    "https://bitcoinist.com/feed/",
    "https://news.bitcoin.com/feed/",
    "https://decrypt.co/feed",
]

# Scoring thresholds (1-10 scale)
SCORE_HIGH = 7      # Auto-ready for posting
SCORE_MEDIUM = 4    # Goes to review queue
# Below SCORE_MEDIUM = archived

# Database path for deduplication
DB_PATH = Path(__file__).parent / "data" / "articles.db"

# Silver Bullet space path
# Change this to your Silver Bullet space directory
SILVERBULLET_SPACE = os.environ.get("SILVERBULLET_SPACE", "~/data/notes")

# Claude model to use
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# How many articles to process per run
MAX_ARTICLES_PER_RUN = 20

# Your content style/voice guidelines
CONTENT_STYLE = """
You write as a Bitcoin-focused content creator. Your style is:
- Knowledgeable but accessible
- Focused on Bitcoin (not crypto in general)
- Signal over noise - cut through hype
- Balanced perspective - acknowledge both opportunities and risks
- No shilling or price predictions
"""
