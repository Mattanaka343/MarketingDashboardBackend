from datetime import date
import aiomysql

METRIC_COL = {
    "impressions":    "impressions",
    "engagementRate": "engagementRate",
    "engagements":    "engagements",
    "reactions":      "reactions",
}

async def get_conn():
    return await aiomysql.connect(
        host="localhost",
        user="root",
        password="#KOF.Terry13",
        db="mkt",
        cursorclass=aiomysql.DictCursor,  
    )


async def fetch_overview_metrics(
    brand: str, channel: str, since: date, until: date
) -> dict:
    """
    Returns aggregate metrics for a single time window.
    Called twice by the service — once for current period,
    once for previous period — so the service can compute deltas.
    """
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                SUM(impressions)                    AS impressions,
                AVG(engagementRate)                 AS engagement_rate,
                SUM(followersGained)                AS followers_gained,
                MAX(followersTotal)                 AS followers_total
            FROM Metrics
            WHERE acc  = %s
              AND (%s = 'all' OR chan = %s)
              AND date >= %s
              AND date <  %s
        """, (brand, channel, channel, since, until))
        row = await cur.fetchone()
    conn.close()
    return row

async def fetch_timeseries(
    brand: str, channel: str, since: date, until: date, metric: str
) -> list:
    col = METRIC_COL[metric]  

    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(f"""
            SELECT
                date,
                SUM(CASE WHEN chan = 'lin' THEN {col} ELSE 0 END) AS linkedin,
                SUM(CASE WHEN chan = 'x'   THEN {col} ELSE 0 END) AS x
            FROM Metrics
            WHERE acc = %s
              AND (%s = 'all' OR chan = %s)
              AND date >= %s
              AND date <  %s
            GROUP BY date
            ORDER BY date ASC
        """, (brand, channel, channel, since, until))
        rows = await cur.fetchall()
    conn.close()
    return rows

async def fetch_followers_by_week(
    brand: str, channel: str, since: date, until: date
) -> list:
    """
    Returns net new followers grouped by ISO week.
    YEARWEEK ensures weeks don't bleed across years.
    """
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                YEARWEEK(date, 1)       AS week_key,
                MIN(date)               AS week_start,
                SUM(followersGained)    AS followers
            FROM Metrics
            WHERE acc  = %s
              AND (%s = 'all' OR chan = %s)
              AND date >= %s
              AND date <  %s
            GROUP BY YEARWEEK(date, 1)
            ORDER BY week_key ASC
        """, (brand, channel, channel, since, until))
        rows = await cur.fetchall()
    conn.close()
    return rows


async def fetch_top_posts(
    brand: str, channel: str, since: date, until: date, limit: int
) -> list:
    """
    Returns the top N posts ranked by engagementRate descending.
    """
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                row_hash        AS id,
                chan            AS channel,
                postText        AS text,
                postUrl         AS url,
                date            AS published_at,
                impressions,
                reactions       AS likes,
                comments,
                shares,
                engagementRate  AS engagement_rate
            FROM Posts
            WHERE acc  = %s
              AND (%s = 'all' OR chan = %s)
              AND date >= %s
              AND date <  %s
            ORDER BY engagementRate DESC
            LIMIT %s
        """, (brand, channel, channel, since, until, limit))
        rows = await cur.fetchall()
    conn.close()
    return rows


async def fetch_post_clusters(brand: str, channel: str) -> list:
    """
    Returns the UMAP projection for every post.
    No date filter — clusters are computed over all posts.
    umap_x, umap_y, and pillar are already stored in your PostDF.
    """
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                row_hash        AS post_id,
                postText        AS text,
                umap_x          AS x,
                umap_y          AS y,
                type            AS cluster
            FROM Posts
            WHERE acc = %s
              AND (%s = 'all' OR chan = %s)
              AND umap_x IS NOT NULL
              AND umap_y IS NOT NULL
        """, (brand, channel, channel))
        rows = await cur.fetchall()
    conn.close()
    return rows


async def fetch_post_terms(
    brand: str, channel: str, since: date, until: date
) -> list:
    """
    Returns raw term scores from your terms table.
    """
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                row_hash    AS term_id,  
                term,
                engagement_score
            FROM Terms
            WHERE acc  = %s
              AND (%s = 'all' OR chan = %s)
        """, (brand, channel, channel))
        rows = await cur.fetchall()
    conn.close()
    return rows
