"""Content generation using Claude API"""

import json
from dataclasses import dataclass
from anthropic import Anthropic


@dataclass
class GeneratedContent:
    """Generated social media content."""
    tweet: str           # Single tweet (< 280 chars)
    thread: str          # Twitter thread (numbered)
    linkedin: str        # LinkedIn post


GENERATION_PROMPT = """You are a Bitcoin content creator. Generate social media posts about this article.

{style_guide}

Article Title: {title}
Article Source: {source}
Article Summary: {summary}
Article URL: {url}

Generate three versions:

1. TWEET: A single tweet (max 270 chars to leave room for link). Punchy, insightful take.

2. THREAD: A Twitter thread of 3-5 tweets. Start with a hook, explain the significance, end with your take. Number them 1/, 2/, etc.

3. LINKEDIN: A LinkedIn post (150-300 words). More professional tone, add context and analysis.

Important:
- Don't just summarize - add insight and perspective
- No generic engagement bait ("What do you think?")
- Be specific about why this matters
- No price predictions or financial advice
- Focus on Bitcoin, not crypto in general

Respond with JSON:
{{
    "tweet": "<single tweet text>",
    "thread": "<full thread with 1/, 2/, etc>",
    "linkedin": "<linkedin post>"
}}"""


def generate_content(
    client: Anthropic,
    title: str,
    summary: str,
    source: str,
    url: str,
    style_guide: str,
    model: str
) -> GeneratedContent:
    """Generate social media content for an article."""

    prompt = GENERATION_PROMPT.format(
        title=title,
        summary=summary,
        source=source,
        url=url,
        style_guide=style_guide
    )

    response = client.messages.create(
        model=model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()

    # Handle markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        data = json.loads(text)
        return GeneratedContent(
            tweet=data.get("tweet", ""),
            thread=data.get("thread", ""),
            linkedin=data.get("linkedin", "")
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error parsing generated content: {e}")
        print(f"Response was: {text[:500]}")
        return GeneratedContent(tweet="", thread="", linkedin="")
