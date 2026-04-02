from fastapi import APIRouter
from typing import Literal
from dependencies import BrandParam, ChannelParam, PeriodParam, Channel, Period, MetricParam, Metric
from services import overview as overview_service

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("/")
async def get_overview(
    brand:   str = BrandParam,
    channel: Literal["all", "lin", "x"] = ChannelParam,
    period:  Literal["7d", "30d", "90d", "1y"] = PeriodParam,
):
    return await overview_service.get_overview(brand, channel, period)




@router.get("/timeseries")
async def get_timeseries(
    brand:   str    = BrandParam,
    channel: Channel = ChannelParam,
    period:  Period  = PeriodParam,
    metric:  Metric  = MetricParam,   # new
):
    return await overview_service.get_timeseries(brand, channel, period, metric)


@router.get("/followers")
async def get_followers(
    brand:   str = BrandParam,
    channel: Literal["all", "lin", "x"] = ChannelParam,
    period:  Literal["7d", "30d", "90d", "1y"] = PeriodParam,
):
    return await overview_service.get_followers(brand, channel, period)
