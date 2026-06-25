from db import queries

async def get_all_formats() -> list:
    return await queries.fetch_all_formats()

async def get_all_content_pillars() -> list:
    return await queries.fetch_all_content_pillars()

async def get_all_strat_pillars(brand: str) -> list:
    return await queries.fetch_all_strat_pillars(brand)

async def get_pending_posts(brand:str, channel:str) -> list:
    return await queries.fetch_pending_posts(brand,channel)

async def get_unpending_posts(brand:str,channel:str) -> list:
    return await queries.fetch_unpending_posts(brand,channel)

async def get_day_metrics(brand:str, channel:str) -> list:
    return await queries.fetch_day_met_data(brand,channel)

async def add_new_format(format:str) -> None:
    await queries.insert_new_format(format)

async def add_new_strat_pillar(pillar:str, brand:str) -> None:
    brand_id = await queries.fetch_id_from_brand(brand)
    await queries.insert_new_strat_pillar(brand_id,pillar)


async def update_pending_posts(strat_pillar: str, content_pillar:str ,format: str,post_id: str) -> None:
    format_id = await queries.fetch_id_from_format(format)
    format_id = format_id["id"]
    strat_pillar_id = await queries.fetch_id_from_strat_pillar(strat_pillar)
    strat_pillar_id = strat_pillar_id["id"]
    content_pillar_id = await queries.fetch_id_from_content_pillar(content_pillar)
    content_pillar_id = content_pillar_id["id"]


    await queries.update_pending_post(post_id,format_id,strat_pillar_id,content_pillar_id)

    