from utils import analyze_organic_marketing,period_to_date
from db import queries 

async def get_ai_review(brand: str, channel: str, period: str):
    since, until = period_to_date(period)
    data = await queries.fetch_ai_food_data(brand,channel,since,until)
    message = analyze_organic_marketing(data)
    return {'message':message}


