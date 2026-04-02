from db import queries
from utils import period_to_date, period_to_previous_dates


async def get_overview(brand: str, channel: str, period: str) -> dict:
    since, until = period_to_date(period)
    prev_since, prev_until = period_to_previous_dates(period)

    current  = await queries.fetch_overview_metrics(brand, channel, since, until)
    previous = await queries.fetch_overview_metrics(brand, channel, prev_since, prev_until)

    # helper to safely get a numeric value, defaulting to 0 if the period had no data
    def val(row, key):
        return row[key] or 0 if row else 0

    impressions_delta = _pct_change(val(previous, "impressions"),   val(current, "impressions"))
    engagement_delta  = round(val(current, "engagement_rate") - val(previous, "engagement_rate"), 2)
    followers_pct     = _pct_change(val(previous, "followers_gained"), val(current, "followers_gained"))

    return {
        "impressions":       val(current, "impressions"),
        "impressions_delta": impressions_delta,
        "engagement_rate":   val(current, "engagement_rate"),
        "engagement_delta":  engagement_delta,
        "followers_gained":  int(val(current, "followers_gained")),
        "followers_pct":     followers_pct,
    }


async def get_timeseries(brand: str, channel: str, period: str, metric: str) -> list:
    since, until = period_to_date(period)
    return await queries.fetch_timeseries(brand, channel, since, until, metric)


async def get_followers(brand: str, channel: str, period: str) -> list:
    since, until = period_to_date(period)
    return await queries.fetch_followers_by_week(brand, channel, since, until)


def _pct_change(old: float, new: float) -> float:
    if not old:
        return 0.0
    return round((new - old) / old * 100, 1)
