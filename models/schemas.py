from pydantic import BaseModel, Field
from typing import List, Optional

class TravelProfile(BaseModel):
    """Represents a user's stored travel preferences."""
    user_id: str
    interests: List[str] = Field(description="e.g., history, food, nature, nightlife")
    preferred_budget: str = Field(description="e.g., $, $$, $$$, $$$$")
    accessibility_needs: Optional[List[str]] = Field(default=None, description="e.g., wheelchair accessible")
    dietary_restrictions: Optional[List[str]] = Field(default=None, description="e.g., vegan, gluten-free")
    party_size: int = Field(default=1, description="Number of people traveling")

class AgentInput(BaseModel):
    """The input to the LLM agent."""
    user_id: str = Field(description="The ID of the user to fetch the profile for.")
    location: str = Field(description="The target city or specific location (e.g., 'Seattle' or coordinates).")

class PlaceRecommendation(BaseModel):
    """A single place recommendation tailored to the user's profile."""
    name: str = Field(description="Name of the recommended place.")
    address: str = Field(description="Address or location of the place.")
    description: str = Field(description="Brief description of what the place is.")
    category: str = Field(description="Category of the place (e.g., Museum, Restaurant, Park).")
    match_reason: str = Field(description="Specific reason why this place matches the given user's travel profile.")
    rating: Optional[float] = Field(description="Google Maps rating if available.")

class AgentOutput(BaseModel):
    recommendations: List[PlaceRecommendation]

class WeatherRecommendation(BaseModel):
    temperature: str
    conditions: str
    date: str
    dressing_suggestions: str = Field(description="Suggestions for what to wear based on the weather.")

class FunFactRecommendation(BaseModel):
    title: str = Field(description="A catchy, short title for the fun fact.")
    description: str = Field(description="The interesting historical or cultural fun fact about the location.")

class RecommendationsOutput(BaseModel):
    """The final output returned by the agent."""
    recommendations: List[PlaceRecommendation] = Field(description="A list of places matching the user's profile.")
