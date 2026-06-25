import os
import ollama
import json
import asyncio

from datetime import date, timedelta
from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig

load_dotenv()

LLM_MODEL = os.getenv('LLM_MODEL')
GEM_API_KEY = os.getenv('GEMINI_API_KEY')
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

    
async def analyze_organic_marketing(organic_data: list) -> str:
    """
    Analyzes organic social media (LinkedIn, X, IG) and website traffic data 
    using the Google Antigravity SDK agent loop.
    """

    formatted_data = json.dumps(
        organic_data,
        indent=2,
        default=str
    )
    
    # In the Antigravity SDK, system prompts are passed directly 
    # to the LocalAgentConfig as system_instructions.
    system_instructions = (
        "You are an expert Organic Growth Marketer and Social Media Strategist. "
        "Your goal is to analyze organic metrics across LinkedIn, X (Twitter), Instagram, and Web. "
        "Look closely at the relationship between impressions and engagement (Content Quality), "
        "and social traffic vs. web conversions (Funnel Efficiency).\n\n"
        "Structure your response exactly like this:\n"
        "1. **The Headline**: A 1-2 sentence executive summary of the brand's organic health.\n"
        "2. **Platform Breakdown**: Bullet points highlighting the biggest winner and biggest red flag.\n"
        "3. **Content Strategy Adjustments**: What should they post MORE of and LESS of based on the data?\n"
        "4. **Action Items**: Exactly 3 distinct, tactical next steps for next week."
    )
    
    user_prompt = (
        f"Analyze this organic marketing performance data:\n\n{formatted_data}\n\n"
        "Identify which platforms are driving true high-value engagement versus just 'vanity metrics' "
        "(like high views but zero clicks or shares)."
    )
    
    try:
        # Initialize the config with your system framework
        config = LocalAgentConfig(
            api_key=GEM_API_KEY,
            system_instructions=system_instructions
        )
        
        # Spin up the stateful Antigravity agent context
        async with Agent(config) as agent:
            response = await agent.chat(user_prompt)
            # Await the text generation result from the response object
            return await response.text()

    except Exception as e:
        return f"Error analyzing organic data via Antigravity SDK: {str(e)}"