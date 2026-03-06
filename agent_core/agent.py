import os
from google.adk.agents import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import google_search
from google.genai import types
from pydantic import BaseModel
import json

from models.schemas import AgentInput, RecommendationsOutput, WeatherRecommendation, FunFactRecommendation
from agent_core.prompts import SYSTEM_PROMPT, WEATHER_SYSTEM_PROMPT, FUN_FACT_SYSTEM_PROMPT
from utils.profile_fetcher import ProfileFetcher

class AugmentedInput(BaseModel):
    """The input to the LLM step, containing both the location and the active profile."""
    location: str
    profile: str

def fetch_profile_step(input_data: AgentInput) -> AugmentedInput:
    """Pre-processing step to fetch the user profile and merge it into the LLM input."""
    fetcher = ProfileFetcher(mode="mock")
    profile = fetcher.get_profile(input_data.user_id)
    return AugmentedInput(
        location=input_data.location,
        profile=profile.model_dump_json()
    )

maps_search_agent = LlmAgent(
    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    name="maps_search_agent",
    description="Searches for interesting places using Google Search",
    instruction=SYSTEM_PROMPT,
    tools=[google_search],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4
    ),
    input_schema=AugmentedInput,
    output_key="DATA"
)

maps_formatter_agent = LlmAgent(
    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    name="maps_formatter_agent",
    description="Formats the found places into recommendations schema",
    instruction="You are an agent that formats the places data from DATA into the strictly required JSON RecommendationsOutput format. Do not alter the match reasons, just parse them correctly.",
    output_schema=RecommendationsOutput
)

maps_recommender_pipeline = SequentialAgent(
    name="MapsRecommenderPipeline",
    sub_agents=[maps_search_agent, maps_formatter_agent]
)

weather_search_agent = LlmAgent(
    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    name="weather_search_agent",
    description="Fetches weather for a location",
    instruction=WEATHER_SYSTEM_PROMPT,
    tools=[google_search],
    output_key="WEATHER_DATA"
)

weather_formatter_agent = LlmAgent(
    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    name="weather_formatter_agent",
    description="Formats weather and dressing suggestions",
    instruction="Format the WEATHER_DATA into the required WeatherRecommendation JSON schema.",
    output_schema=WeatherRecommendation
)

weather_agent = SequentialAgent(
    name="WeatherPipeline",
    sub_agents=[weather_search_agent, weather_formatter_agent]
)

fun_fact_search_agent = LlmAgent(
    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    name="fun_fact_search_agent",
    description="Finds an interesting fun fact for a location",
    instruction=FUN_FACT_SYSTEM_PROMPT,
    tools=[google_search],
    output_key="FUN_FACT_DATA"
)

fun_fact_formatter_agent = LlmAgent(
    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    name="fun_fact_formatter_agent",
    description="Formats a fun fact",
    instruction="Format the FUN_FACT_DATA into the required FunFactRecommendation JSON schema.",
    output_schema=FunFactRecommendation
)

fun_fact_agent = SequentialAgent(
    name="FunFactPipeline",
    sub_agents=[fun_fact_search_agent, fun_fact_formatter_agent]
)

__all__ = ["maps_recommender_pipeline", "fetch_profile_step", "weather_agent", "fun_fact_agent"]
