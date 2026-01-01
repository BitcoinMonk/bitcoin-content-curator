#!/usr/bin/env python3
"""
Bitcoin Content Curator - CLI Entry Point

Watches Bitcoin news feeds, scores articles with AI, and generates
social media content drafts.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import run_pipeline
import config


def main():
    parser = argparse.ArgumentParser(
        description="Bitcoin Content Curator - AI-powered content curation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing to Silver Bullet"
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=config.MAX_ARTICLES_PER_RUN,
        help=f"Max articles to process (default: {config.MAX_ARTICLES_PER_RUN})"
    )
    parser.add_argument(
        "--score-high",
        type=float,
        default=config.SCORE_HIGH,
        help=f"Score threshold for auto-ready (default: {config.SCORE_HIGH})"
    )
    parser.add_argument(
        "--score-medium",
        type=float,
        default=config.SCORE_MEDIUM,
        help=f"Score threshold for review queue (default: {config.SCORE_MEDIUM})"
    )
    parser.add_argument(
        "--space",
        type=str,
        default=config.SILVERBULLET_SPACE,
        help=f"Silver Bullet space path (default: {config.SILVERBULLET_SPACE})"
    )

    args = parser.parse_args()

    # Check API key
    if not config.ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Export it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    print("=" * 50)
    print("Bitcoin Content Curator")
    print("=" * 50)
    print(f"Model: {config.CLAUDE_MODEL}")
    print(f"Feeds: {len(config.RSS_FEEDS)}")
    print(f"Max articles: {args.max_articles}")
    print(f"Score thresholds: High >= {args.score_high}, Medium >= {args.score_medium}")
    print(f"Silver Bullet space: {args.space}")
    if args.dry_run:
        print("MODE: DRY RUN (no files written)")
    print("=" * 50)
    print()

    try:
        run_pipeline(
            api_key=config.ANTHROPIC_API_KEY,
            feeds=config.RSS_FEEDS,
            db_path=config.DB_PATH,
            silverbullet_space=args.space,
            model=config.CLAUDE_MODEL,
            style_guide=config.CONTENT_STYLE,
            score_high=args.score_high,
            score_medium=args.score_medium,
            max_articles=args.max_articles,
            dry_run=args.dry_run
        )
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
