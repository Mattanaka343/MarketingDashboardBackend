from datetime import date
from dotenv import load_dotenv

import os
import aiomysql

load_dotenv()

METRIC_COL = {
    "impressions":    "impressions",
    "engagementRate": "engagementRate",
    "engagements":    "engagements",
    "reactions":      "reactions",
}

BRAND_MAP = {
    "nvai": "Nurvai",
    "buis": "Wexpand",
    "tal": "Wexpand Talent"
}

CHANNEL_MAP = {
    'lin': "LinkedIn",
    'x': 'X',
    'insta' : "Instagram",
    'all' : 'all'
}

async def get_conn():
    return await aiomysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),
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
    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]  
    
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                SUM(m.impressions)                    AS impressions,
                AVG(m.engagementRate)                 AS engagement_rate,
                SUM(m.followersGained)                AS followers_gained,
                MAX(m.followersTotal)                 AS followers_total
            FROM Metrics m
            JOIN SocialMediaAccounts sma
                ON m.account_id = sma.id
            JOIN Brands b 
                ON sma.brand_id = b.id
            WHERE b.name = %s
              AND (%s = 'all' OR sma.channel = %s)
              AND m.date >= %s
              AND m.date <  %s
        """, (brand, channel, channel, since, until))
        row = await cur.fetchone()
    conn.close()
    return row

async def fetch_timeseries(
    brand: str, channel: str, since: date, until: date, metric: str
) -> list:
    col = METRIC_COL[metric]
    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]  

    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(f"""
            SELECT
                m.date,
                SUM(CASE WHEN sma.channel = 'LinkedIn' THEN {col} ELSE 0 END) AS linkedin,
                SUM(CASE WHEN sma.channel = 'X'   THEN {col} ELSE 0 END) AS x,
                SUM(CASE WHEN sma.channel = 'Instagram' THEN {col} ELSE 0 END) AS instagram
            FROM Metrics m
            JOIN SocialMediaAccounts sma
                ON m.account_id = sma.id
            JOIN Brands b
                On sma.brand_id = b.id
            WHERE b.name = %s
              AND (%s = 'all' OR sma.channel = %s)
              AND m.date >= %s
              AND m.date <  %s
            GROUP BY m.date
            ORDER BY m.date ASC
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
    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel] 

    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                YEARWEEK(m.date, 1)       AS week_key,
                MIN(m.date)               AS week_start,
                SUM(m.followersGained)    AS followers
            FROM Metrics m
            JOIN SocialMediaAccounts sma
                ON m.account_id = sma.id
            JOIN Brands b
                ON sma.brand_id = b.id
            WHERE b.name = %s
              AND (%s = 'all' OR sma.channel = %s)
              AND m.date >= %s
              AND m.date <  %s
            GROUP BY YEARWEEK(m.date, 1)
            ORDER BY week_key ASC
        """, (brand, channel, channel, since, until))
        rows = await cur.fetchall()
    conn.close()
    return rows


async def fetch_top_posts(
    brand: str, channel: str, since: date, until: date, limit: int, metric: str
    ) -> list:
    """
    Returns the top N posts ranked by engagementRate descending.
    """
    col = METRIC_COL[metric]

    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]  
    
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(f"""
            SELECT
                p.row_hash        AS id,
                sma.channel       AS channel,
                p.postText        AS text,
                p.postUrl         AS url,
                p.date      AS published_at,
                p.impressions,
                p.reactions         AS likes,
                p.comments,
                p.shares,
                p.engagementRate  AS engagement_rate
            FROM Posts p
            JOIN SocialMediaAccounts sma
                ON p.account_id = sma.id
            JOIN Brands b
                ON sma.brand_id = b.id
            WHERE b.name  = %s
              AND (%s = 'all' OR sma.channel = %s)
              AND p.date >= %s
              AND p.date <  %s
            ORDER BY p.{col} DESC
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
    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]  

    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                p.row_hash        AS post_id,
                p.postText        AS text,
                p.umap_x          AS x,
                p.umap_y          AS y,
                f.format            AS cluster
            FROM Posts p
            JOIN Formats f
                ON p.format_id = f.id
            JOIN SocialMediaAccounts sma
                ON p.account_id = sma.id
            JOIN Brands b
                ON sma.brand_id = b.id
            WHERE b.name = %s
              AND (%s = 'all' OR sma.channel = %s)
              AND p.umap_x IS NOT NULL
              AND p.umap_y IS NOT NULL
        """, (brand, channel, channel))
        rows = await cur.fetchall()
    conn.close()
    return rows


async def fetch_post_terms(
    brand: str, channel: str
) -> list:
    """
    Returns raw term scores from your terms table.
    """
    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]

    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT
                t.row_hash    AS term_id,  
                t.term,
                t.engagement_score
            FROM Terms t
            JOIN SocialMediaAccounts sma
                ON t.account_id = sma.id
            JOIN Brands b 
                ON sma.brand_id = b.id
            WHERE b.name  = %s
              AND (%s = 'all' OR sma.channel = %s)
        """, (brand, channel, channel))
        rows = await cur.fetchall()
    conn.close()
    return rows

async def insert_new_format(format: str) -> None:
    conn  = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO Formats (format)
            VALUES (%s)
            """, (format,)
        )
    
    await conn.commit()
    conn.close()

async def insert_new_strat_pillar(brand_id: int, pillar: str) -> None:
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO StrategyPillars (brand_id, pillar)
            VALUES (%s, %s)
            """,(brand_id,pillar)
        ) 
    
    await conn.commit()
    conn.close()

async def insert_new_utm(brand_id:int, source: str, campaing: str, medium:str) -> None:
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO Sources (brand_id, source, campaign, medium)
            VALUEES (%s,%s,%s,%s)
            """,(brand_id,source,campaing,medium)
        )
    await conn.commit()
    conn.close()

async def fetch_id_from_brand(brand:str ) -> int:
    conn = await get_conn()
    brand = BRAND_MAP[brand]
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id
            FROM Brands
            WHERE name = %s
            """,(brand,)
        )
        result = await cur.fetchone()
    conn.close
    return result

async def fetch_displayed_links(brand:str) -> list:
    conn = await get_conn()
    brand = BRAND_MAP[brand]
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT  s.source         AS source,
                    s.medium         AS medium,
                    s.campaign       AS campaign
            FROM sources s
            JOIN Brands b 
                ON s.brand_id = b.id 
            WHERE b.name = %s
            """, (brand,)
        )
        rows = await cur.fetchall()
    conn.close()
    return rows

async def fetch_pending_posts(brand:str,channel:str)->list:
    conn = await get_conn()
    brand =  BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT  p.postText     AS text,
                    p.postUrl      AS url,
                    p.date         AS date,
                    b.name         AS brand,
                    sma.channel    AS channel,
                    p.row_hash     AS id
            FROM Posts p
            JOIN SocialMediaAccounts sma
                ON p.account_id = sma.id
            JOIN Brands b
                ON sma.brand_id = b.id
            
            WHERE b.name = %s                      AND
                  (%s = 'all' OR sma.channel = %s) AND
                  (p.format_id IS NULL)            AND
                  (p.content_pillar_id IS NULL)    AND
                  (p.strategy_pillar_id IS NULL)   
            """, (brand,channel,channel)
        )
        rows = await cur.fetchall()
    conn.close()
    return rows

async def fetch_unpending_posts(brand:str, channel:str) ->list:
    conn = await get_conn()
    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT  p.postText      AS text,
                    p.postUrl       AS url,
                    p.date          AS date,
                    b.name          AS brand,
                    sma.channel     AS channel,
                    f.format        AS format,
                    stp.pillar      AS strategy_pillar,
                    ctp.pillar      AS content_pillar,
                    p.row_hash      AS id

            FROM Posts p
            JOIN SocialMediaAccounts sma
                ON p.account_id = sma.id
            JOIN Brands b
                ON sma.brand_id = b.id
            JOIN Formats f
                ON p.format_id = f.id
            JOIN StrategyPillars stp
                ON p.strategy_pillar_id = stp.id
            JOIN ContentPillars ctp
                ON p.content_pillar_id = ctp.id

            WHERE b.name = %s           AND
                  (%s = 'all' OR sma.channel = %s)
            """, (brand,channel,channel)
        )
        rows = await cur.fetchall()
    conn.close()
    return rows

async def fetch_day_met_data(brand:str, channel:str) -> list:
    conn = await get_conn()
    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT  m.impressions           AS impressions,
                    m.engagementRate        AS engagement_rate,
                    m.engagements           AS engagements,
                    m.clicks                AS clicks,
                    m.row_hash              AS id,
                    m.date                  AS date,
                    b.name                  AS brand,
                    sma.channel             AS channel

            FROM Metrics m
            JOIN SocialMediaAccounts sma
                ON m.account_id = sma.id
            JOIN Brands b
                ON sma.brand_id = b.id

            WHERE   b.name = %s           AND
                    (%s = 'all' OR sma.channel = %s)
            """, (brand,channel,channel)
        )
        rows = await cur.fetchall()
    conn.close()
    return rows

async def fetch_all_formats() -> list:
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT format
            FROM Formats
            """
        )
        rows = await cur.fetchall()
    conn.close()
    return rows 

async def fetch_all_strat_pillars(brand: str) -> list:
    conn = await get_conn()
    brand = BRAND_MAP[brand]
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT pillar
            FROM StrategyPillars
            """
        )
        rows = await cur.fetchall()
    conn.close()
    return rows

async def fetch_all_content_pillars() ->list:
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT pillar
            FROM ContentPillars
            """
        )
        rows = await cur.fetchall()
    conn.close()
    return rows

async def fetch_id_from_format(format:str) -> int:
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id
            FROM Formats
            WHERE format = %s
            """,(format,)
        )
        result = await cur.fetchone()
    conn.close()
    return result

async def fetch_id_from_strat_pillar(pillar:str) ->int:
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id
            FROM StrategyPillars
            WHERE pillar = %s
            """, (pillar,)
        )
        result = await cur.fetchone()
    conn.close()
    return result

async def fetch_id_from_content_pillar(pillar:str) -> int:
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id
            FROM ContentPillars
            WHERE pillar = %s 
            """, (pillar,)
        )
        result = await cur.fetchone()
    conn.close()
    return result

async def update_pending_post(post_id: str,format_id: int,strat_pillar_id: int,content_pillar_id: int) -> None:
    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            UPDATE Posts
            SET format_id = %s,
                content_pillar_id = %s,
                strategy_pillar_id = %s
            WHERE row_hash = %s
            """,(format_id,content_pillar_id,strat_pillar_id,post_id)
        )
    await conn.commit()
    conn.close()

async def fetch_ai_food_data(brand:str,channel:str,since:date, until:date) -> list:

    brand = BRAND_MAP[brand]
    channel = CHANNEL_MAP[channel]

    conn = await get_conn()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT  m.date                  AS date,
                    m.impressions           AS impressions,
                    m.bookmarks             AS bookmarks,
                    m.clicks                AS clicks,
                    m.engagements           AS engagements,
                    m.engagementRate        AS engagementRate,
                    m.followersGained       AS followersGained,
                    m.followersTotal        AS followersTotal,
                    m.shares                AS shares,
                    m.unfollows             AS unfollows,
                    b.name                  AS brand,
                    sma.channel             AS channel

            FROM Metrics m
            JOIN SocialMediaAccounts sma
                ON m.account_id = sma.id
            JOIN Brands b
                ON sma.brand_id = b.id
            
            WHERE   b.name = %s                           AND
                    ('all' = %s OR sma.channel = %s)      AND
                    m.date >= %s                          AND
                    m.date <= %s          
            """,(brand,channel,channel,since,until)
        )

        rows = await cur.fetchall()

    conn.close()
    return rows



