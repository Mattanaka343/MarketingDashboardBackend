from fastapi import APIRouter
from dependencies import BrandParam, ChannelParam, Channel, Brand
from services import operations as op_service

router = APIRouter(prefix = "/api/operations", tags = ["operations"])

@router.get("/allformats")
async def get_all_formats() -> list:
    return await op_service.get_all_formats()

@router.get("/allcontentpillars")
async def get_all_content_pillars() -> list:
    return await op_service.get_all_content_pillars()

@router.get("/allstratpillars")
async def get_all_strat_pillars(brand: Brand = BrandParam) -> list:
    return await op_service.get_all_strat_pillars(brand)

@router.get("/pendingposts")
async def get_pending_posts(brand: Brand = BrandParam, channel: Channel = ChannelParam) -> list:
    return await op_service.get_pending_posts(brand,channel)

@router.get("/unpendingposts")
async def get_pending_post(brand: Brand = BrandParam, channel: Channel = ChannelParam)-> list:
    return await op_service.get_unpending_posts(brand,channel)

@router.get("/metrics")
async def get_metrics(brand: Brand = BrandParam, channel: Channel = ChannelParam) -> list:
    return await op_service.get_day_metrics(brand,channel)

@router.post("/format")
async def add_format(format: str) -> dict:
    await op_service.add_new_format(format)
    return {"ok": True, "format": format}

@router.post("/stratpillar")
async def add_new_strat_pillar(pillar: str, brand:str) -> dict:
    await op_service.add_new_strat_pillar(pillar, brand)
    return {"ok": True, "pillar":pillar, "brand":brand}

@router.post("/updatependingpost")
async def update_pending_post(strat_pillar:str ,content_pillar: str,format: str, post_id:str) -> dict:
    await op_service.update_pending_posts(strat_pillar,content_pillar,format,post_id)
    return {"ok": True, "post": post_id}