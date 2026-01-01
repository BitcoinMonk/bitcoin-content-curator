"""Main content curation pipeline"""

from anthropic import Anthropic
from pathlib import Path

from .fetcher import fetch_all_feeds, Article
from .scorer import score_article
from .generator import generate_content
from .database import (
    get_connection,
    article_exists,
    insert_article,
    update_score,
    insert_content
)
from .output import write_to_silverbullet


def run_pipeline(
    api_key: str,
    feeds: list[str],
    db_path: Path,
    silverbullet_space: str,
    model: str,
    style_guide: str,
    score_high: float = 7,
    score_medium: float = 4,
    max_articles: int = 20,
    dry_run: bool = False
) -> dict:
    """
    Run the full content curation pipeline.

    Returns:
        dict with stats: processed, scored, generated, by_category
    """
    stats = {
        "fetched": 0,
        "new": 0,
        "skipped_duplicate": 0,
        "scored": 0,
        "generated": 0,
        "ready": 0,
        "review": 0,
        "archive": 0
    }

    # Initialize
    client = Anthropic(api_key=api_key)
    conn = get_connection(db_path)

    print(f"Fetching articles from {len(feeds)} feeds...")

    processed = 0
    for article in fetch_all_feeds(feeds):
        stats["fetched"] += 1

        # Check if already processed
        if article_exists(conn, article.url):
            stats["skipped_duplicate"] += 1
            continue

        stats["new"] += 1

        # Respect max articles limit
        if processed >= max_articles:
            print(f"Reached max articles limit ({max_articles})")
            break

        processed += 1
        print(f"\n[{processed}] Processing: {article.title[:60]}...")

        # Insert article
        article_id = insert_article(
            conn,
            url=article.url,
            title=article.title,
            source=article.source,
            published_at=article.published_at
        )

        # Score the article
        print("  Scoring...")
        score_result = score_article(
            client=client,
            title=article.title,
            summary=article.summary,
            source=article.source,
            model=model
        )
        stats["scored"] += 1

        print(f"  Score: {score_result.score}/10 - {score_result.reason[:50]}...")

        # Determine category
        if score_result.score >= score_high:
            category = "ready"
            status = "ready"
            stats["ready"] += 1
        elif score_result.score >= score_medium:
            category = "review"
            status = "review"
            stats["review"] += 1
        else:
            category = "archive"
            status = "archived"
            stats["archive"] += 1

        # Update score in database
        update_score(conn, article_id, score_result.score, score_result.reason, status)

        # Generate content for high and medium scores
        tweet = thread = linkedin = None
        if score_result.score >= score_medium and score_result.is_bitcoin_relevant:
            print("  Generating content...")
            content = generate_content(
                client=client,
                title=article.title,
                summary=article.summary,
                source=article.source,
                url=article.url,
                style_guide=style_guide,
                model=model
            )
            stats["generated"] += 1

            tweet = content.tweet
            thread = content.thread
            linkedin = content.linkedin

            # Store in database
            if tweet:
                insert_content(conn, article_id, "tweet", tweet)
            if thread:
                insert_content(conn, article_id, "thread", thread)
            if linkedin:
                insert_content(conn, article_id, "linkedin", linkedin)

        # Write to Silver Bullet
        if not dry_run:
            print(f"  Writing to Silver Bullet ({category})...")
            write_to_silverbullet(
                space_path=silverbullet_space,
                category=category,
                title=article.title,
                url=article.url,
                source=article.source,
                score=score_result.score,
                score_reason=score_result.reason,
                tweet=tweet,
                thread=thread,
                linkedin=linkedin
            )
        else:
            print(f"  [DRY RUN] Would write to {category}")

    conn.close()

    print("\n" + "=" * 50)
    print("Pipeline complete!")
    print(f"  Fetched: {stats['fetched']} articles")
    print(f"  New: {stats['new']} (skipped {stats['skipped_duplicate']} duplicates)")
    print(f"  Scored: {stats['scored']}")
    print(f"  Generated content for: {stats['generated']}")
    print(f"  Ready to post: {stats['ready']}")
    print(f"  Needs review: {stats['review']}")
    print(f"  Archived: {stats['archive']}")

    return stats
