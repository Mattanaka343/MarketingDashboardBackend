from datetime import date, timedelta

PERIOD_DAYS = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}


def period_to_date(period: str) -> tuple[date, date]:
    """
    Returns (since, until) for the current period.
    e.g. "30d" -> (30 days ago, today)
    """
    today = date.today()
    since = today - timedelta(days=PERIOD_DAYS[period])
    return since, today


def period_to_previous_dates(period: str) -> tuple[date, date]:
    """
    Returns (since, until) for the previous period -- used to compute deltas.
    e.g. "30d" -> (60 days ago, 30 days ago)
    """
    today = date.today()
    days  = PERIOD_DAYS[period]
    until = today - timedelta(days=days)
    since = until - timedelta(days=days)
    return since, until
