from fastapi import APIRouter, Query
from typing import Literal
from dependencies import BrandParam, ChannelParam, PeriodParam
from services import posts as posts_service

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("/top")
async def get_top_posts(
    brand:   str = BrandParam,
    channel: Literal["all", "lin", "x"] = ChannelParam,
    period:  Literal["7d", "30d", "90d", "1y"] = PeriodParam,
    limit:   int = Query(10, ge=1, le=50),
):
    return await posts_service.get_top_posts(brand, channel, period, limit)


@router.get("/clusters")
async def get_clusters(
    brand:   str = BrandParam,
    channel: Literal["all", "lin", "x"] = ChannelParam,
):
    return await posts_service.get_clusters(brand, channel)


@router.get("/terms")
async def get_best_terms(
    brand:   str = BrandParam,
    channel: Literal["all", "lin", "x"] = ChannelParam,
    period:  Literal["7d", "30d", "90d", "1y"] = PeriodParam,
    limit:   int = Query(20, ge=5, le=100),
):
    return await posts_service.get_best_terms(brand, channel, period, limit)
