"""Article scoring using Claude API"""

import json
from dataclasses import dataclass
from anthropic import Anthropic


@dataclass
class ScoreResult:
    """Result of scoring an article."""
    score: float
    reason: str
    is_bitcoin_relevant: bool


SCORING_PROMPT = """You are evaluating articles for a Bitcoin-focused content curator.

Rate this article on a scale of 1-10 based on:
- Bitcoin relevance (is it specifically about Bitcoin, not general crypto?)
- Newsworthiness (is this significant/interesting news?)
- Educational value (does it explain something useful?)
- Signal vs noise (substance over hype/clickbait?)

Heavily penalize:
- Articles primarily about altcoins, memecoins, or general "crypto"
- Pure price speculation or prediction articles
- Sponsored content or obvious shilling
- Rehashed news without new information

Boost:
- Technical Bitcoin developments (protocol, Lightning, mining)
- Adoption news (companies, countries, institutions)
- Regulatory developments affecting Bitcoin
- Educational deep-dives on Bitcoin concepts
- Original analysis or research

Article Title: {title}
Article Source: {source}
Article Summary: {summary}

Respond with JSON only:
{{
    "score": <1-10>,
    "reason": "<brief explanation>",
    "is_bitcoin_relevant": <true/false>
}}"""


def score_article(
    client: Anthropic,
    title: str,
    summary: str,
    source: str,
    model: str
) -> ScoreResult:
    """Score an article using Claude."""

    prompt = SCORING_PROMPT.format(
        title=title,
        summary=summary,
        source=source
    )

    response = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON response
    text = response.content[0].text.strip()

    # Handle markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        data = json.loads(text)
        return ScoreResult(
            score=float(data.get("score", 1)),
            reason=data.get("reason", "No reason provided"),
            is_bitcoin_relevant=data.get("is_bitcoin_relevant", False)
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error parsing score response: {e}")
        print(f"Response was: {text}")
        return ScoreResult(score=1, reason="Failed to parse", is_bitcoin_relevant=False)
