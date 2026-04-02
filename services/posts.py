from db import queries
from utils import period_to_date


async def get_top_posts(brand: str, channel: str, period: str, limit: int) -> list:
    since, until = period_to_date(period)
    return await queries.fetch_top_posts(brand, channel, since, until, limit)


async def get_clusters(brand: str, channel: str) -> list:
    return await queries.fetch_post_clusters(brand, channel)


async def get_best_terms(brand: str, channel: str, period: str, limit: int) -> list:
    since, until = period_to_date(period)
    rows = await queries.fetch_post_terms(brand, channel, since, until)

    if not rows:
        return []

    max_score = max(r["engagement_score"] for r in rows)
    if max_score == 0:
        return []

    normalised = [
        {
            "id": r["term_id"],
            "term":  r["term"],
            "score": round(r["engagement_score"] / max_score, 2),
        }
        for r in rows
        if r["engagement_score"] > 0
    ]

    return sorted(normalised, key=lambda x: x["score"], reverse=True)[:limit]
