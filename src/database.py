"""Database module for tracking processed articles"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
import hashlib


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _init_tables(conn)
    return conn


def _init_tables(conn: sqlite3.Connection) -> None:
    """Initialize database tables."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_hash TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            source TEXT,
            published_at TEXT,
            fetched_at TEXT NOT NULL,
            score REAL,
            score_reason TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS generated_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles(id)
        );

        CREATE INDEX IF NOT EXISTS idx_articles_url_hash ON articles(url_hash);
        CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
        CREATE INDEX IF NOT EXISTS idx_articles_score ON articles(score);
    """)
    conn.commit()


def url_hash(url: str) -> str:
    """Generate hash for URL deduplication."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def article_exists(conn: sqlite3.Connection, url: str) -> bool:
    """Check if article URL has been processed."""
    cursor = conn.execute(
        "SELECT 1 FROM articles WHERE url_hash = ?",
        (url_hash(url),)
    )
    return cursor.fetchone() is not None


def insert_article(
    conn: sqlite3.Connection,
    url: str,
    title: str,
    source: str,
    published_at: Optional[str] = None
) -> int:
    """Insert new article, return ID."""
    cursor = conn.execute(
        """INSERT INTO articles (url_hash, url, title, source, published_at, fetched_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (url_hash(url), url, title, source, published_at, datetime.utcnow().isoformat())
    )
    conn.commit()
    return cursor.lastrowid


def update_score(
    conn: sqlite3.Connection,
    article_id: int,
    score: float,
    reason: str,
    status: str
) -> None:
    """Update article score and status."""
    conn.execute(
        """UPDATE articles SET score = ?, score_reason = ?, status = ? WHERE id = ?""",
        (score, reason, status, article_id)
    )
    conn.commit()


def insert_content(
    conn: sqlite3.Connection,
    article_id: int,
    content_type: str,
    content: str
) -> int:
    """Insert generated content for an article."""
    cursor = conn.execute(
        """INSERT INTO generated_content (article_id, content_type, content)
           VALUES (?, ?, ?)""",
        (article_id, content_type, content)
    )
    conn.commit()
    return cursor.lastrowid


def get_articles_by_status(conn: sqlite3.Connection, status: str) -> list[dict]:
    """Get all articles with given status."""
    cursor = conn.execute(
        """SELECT a.*,
                  (SELECT content FROM generated_content WHERE article_id = a.id AND content_type = 'tweet') as tweet,
                  (SELECT content FROM generated_content WHERE article_id = a.id AND content_type = 'thread') as thread,
                  (SELECT content FROM generated_content WHERE article_id = a.id AND content_type = 'linkedin') as linkedin
           FROM articles a
           WHERE a.status = ?
           ORDER BY a.score DESC, a.created_at DESC""",
        (status,)
    )
    return [dict(row) for row in cursor.fetchall()]
