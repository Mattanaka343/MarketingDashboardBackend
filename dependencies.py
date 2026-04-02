from fastapi import Query
from typing import Literal



MetricParam = Query("impressions", description="Which metric to plot on the timeline")
BrandParam   = Query("nvai",    description="nvai, buis or tal")
ChannelParam = Query("all",  description="'all', 'lin', or 'x'")
PeriodParam  = Query("90d",  description="'7d', '30d', '90d', or '1y'")

# Type aliases — use these in function signatures for consistent validation
Channel = Literal["all", "lin", "x"]
Period  = Literal["7d", "30d", "90d", "1y"]
Metric = Literal["impressions", "engagementRate", "engagements", "reactions"]