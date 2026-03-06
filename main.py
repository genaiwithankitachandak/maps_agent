import os
import logging
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load env variables (e.g., GOOGLE_API_KEY)
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Attempt to load ADK dependencies
try:
    from agent_core.agent import maps_recommender_pipeline, fetch_profile_step, weather_agent, fun_fact_agent
    from models.schemas import AgentInput, WeatherRecommendation, FunFactRecommendation
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from typing import Optional
    import uuid
    logger.info("Successfully imported ADK and agent modules.")
except Exception as e:
    logger.error(f"Import error: {e}")
    raise

# Build FastAPI app explicitly with ADK if we want full UI endpoints
try:
    agent_path = os.path.join(os.path.dirname(__file__), "agent_core")
    app = get_fast_api_app(agent_dir=agent_path, web=True)
    logger.info("ADK FastAPI app created successfully.")
except Exception as e:
    logger.error(f"Failed to create ADK FastAPI app. Fallback to basic FastAPI. Error: {e}")
    app = FastAPI()

# Add CORS middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunPayload(BaseModel):
    user_id: str
    location: str

class WeatherPayload(BaseModel):
    location: str
    date: Optional[str] = "today"
    
class FunFactPayload(BaseModel):
    location: str

@app.post("/weather")
async def get_weather(payload: WeatherPayload):
    """
    Endpoint to trigger the standalone weather_agent.
    """
    session_service = InMemorySessionService()
    session_id = f"weather_session_{uuid.uuid4()}"
    await session_service.create_session(
        app_name="maps_agent",
        user_id="anonymous",
        session_id=session_id
    )
    runner = Runner(agent=weather_agent, app_name="maps_agent", session_service=session_service)
    
    prompt = f"Location: {payload.location}\\nDate: {payload.date}"
    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events = runner.run(user_id="anonymous", session_id=session_id, new_message=content)
    
    final_response = None
    for event in events:
        if event.is_final_response() and event.author == "weather_formatter_agent" and event.content and event.content.parts:
            final_response = event.content.parts[0].text
            
    if final_response:
        import json
        try:
            parsed = json.loads(final_response)
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse weather JSON: {e}")
            return {"error": "Failed to parse"}
            
    return {"error": "No response"}

@app.post("/funfact")
async def get_fun_fact(payload: FunFactPayload):
    """
    Endpoint to trigger the standalone fun_fact_agent.
    """
    session_service = InMemorySessionService()
    session_id = f"funfact_session_{uuid.uuid4()}"
    await session_service.create_session(
        app_name="maps_agent",
        user_id="anonymous",
        session_id=session_id
    )
    runner = Runner(agent=fun_fact_agent, app_name="maps_agent", session_service=session_service)
    
    prompt = f"Location: {payload.location}"
    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events = runner.run(user_id="anonymous", session_id=session_id, new_message=content)
    
    final_response = None
    for event in events:
        if event.is_final_response() and event.author == "fun_fact_formatter_agent" and event.content and event.content.parts:
            final_response = event.content.parts[0].text
            
    if final_response:
        import json
        try:
            parsed = json.loads(final_response)
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse fun fact JSON: {e}")
            return {"error": "Failed to parse"}
            
    return {"error": "No response"}

@app.post("/recommend")
async def recommend_places(payload: RunPayload):
    """
    Standard FastAPI endpoint to manually handle mapping and execution.
    """
    agent_input = AgentInput(user_id=payload.user_id, location=payload.location)
    augmented_input = fetch_profile_step(agent_input)
    
    # Run agent
    session_service = InMemorySessionService()
    session_id = f"session_{uuid.uuid4()}"
    await session_service.create_session(
        app_name="maps_agent",
        user_id=payload.user_id,
        session_id=session_id
    )
    runner = Runner(agent=maps_recommender_pipeline, app_name="maps_agent", session_service=session_service)
    
    content = types.Content(role='user', parts=[types.Part(text=augmented_input.model_dump_json())])
    events = runner.run(user_id=payload.user_id, session_id=session_id, new_message=content)
    
    # Extract the final output from the agent events
    final_response = None
    for event in events:
        if event.is_final_response():
            if event.author == "maps_formatter_agent" and event.content and event.content.parts:
                final_response = event.content.parts[0].text
    
    logger.info(f"Raw final_response from agent: {final_response}")
    if final_response:
        import json
        try:
            parsed = json.loads(final_response)
            logger.info(f"Parsed JSON returning to frontend: {parsed}")
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {"recommendations": []}
    logger.warning("Agent returned empty final_response")
    return {"recommendations": []}

@app.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    from utils.profile_fetcher import ProfileFetcher
    from fastapi import HTTPException
    
    fetcher = ProfileFetcher(mode="bq")
    try:
        profile = fetcher.get_profile(user_id)
        return profile.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Profile not found: {str(e)}")

async def manual_run():
    """CLI execution for local testing."""
    test_user_id = "user_123" # Uses vegan, science, museums mocked profile
    test_location = "Seattle, WA"
    
    logger.info(f"Running manual test for user '{test_user_id}' in '{test_location}'")
    
    agent_input = AgentInput(user_id=test_user_id, location=test_location)
    augmented_input = fetch_profile_step(agent_input)
    
    logger.info(f"Augmented Input: {augmented_input.model_dump_json(indent=2)}")
    
    session_service = InMemorySessionService()
    session_id = f"session_{uuid.uuid4()}"
    await session_service.create_session(
        app_name="maps_agent",
        user_id=test_user_id,
        session_id=session_id
    )
    runner = Runner(agent=maps_recommender_pipeline, app_name="maps_agent", session_service=session_service)
    
    content = types.Content(role='user', parts=[types.Part(text=augmented_input.model_dump_json())])
    events = runner.run(user_id=test_user_id, session_id=session_id, new_message=content)
    
    logger.info("---- AGENT RESULT ----")
    for event in events:
        if event.is_final_response():
            if event.author == "maps_formatter_agent" and event.content and event.content.parts:
                print(event.content.parts[0].text)

# Configure static file serving for the React frontend
# This allows deploying the frontend and backend in a single container
frontend_dist_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(frontend_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="assets")

    # Catch-all route to serve the React SPA index.html
    # Must be placed AFTER all API routes
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Allow API routes to 404 naturally if missed, rather than serving index.html
        if full_path.startswith("recommend") or full_path.startswith("profile") or full_path.startswith("weather") or full_path.startswith("funfact"):
            return JSONResponse(status_code=404, content={"error": "Not Found"})
            
        index_file = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse(status_code=404, content={"error": "Frontend build not found."})
else:
    logger.warning(f"Frontend dist payload missing at {frontend_dist_path}. Only API endpoints will be served.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        uvicorn.run(app, host="0.0.0.0", port=8080)
    else:
        asyncio.run(manual_run())
