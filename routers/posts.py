from fastapi import APIRouter, Query
from typing import Literal
from dependencies import BrandParam, ChannelParam, PeriodParam, MetricParam, Channel, Period, Metric
from services import posts as posts_service

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("/top")
async def get_top_posts(
    brand:   str = BrandParam,
    channel: Channel = ChannelParam,
    period:  Period = PeriodParam,
    limit:   int = Query(10, ge=1, le=50),
    metric: Metric = MetricParam,
):
    return await posts_service.get_top_posts(brand, channel, period, limit, metric)


@router.get("/clusters")
async def get_clusters(
    brand:   str = BrandParam,
    channel: Channel = ChannelParam,
):
    return await posts_service.get_clusters(brand, channel)


@router.get("/terms")
async def get_best_terms(
    brand:   str = BrandParam,
    channel: Channel = ChannelParam,
    period:  Period = PeriodParam,
    limit:   int = Query(20, ge=5, le=100),
):
    return await posts_service.get_best_terms(brand, channel, period, limit)
