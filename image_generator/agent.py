import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from .sub_agents.prompt import image_generation_prompt_agent as image_prompt
from .sub_agents.image import image_generation_agent as image_gen
from .sub_agents.scoring import scoring_images_prompt as scoring_prompt
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService

from google.adk.agents import SequentialAgent

from vertexai.preview.reasoning_engines import AdkApp


llm_auditor = SequentialAgent(
    name='image_generation_scoring_agent',
    description=(
        'Analyzes a news article and creates the image generation prompt, generates the relevant images with imagen3 and scores the images '
    ),
    sub_agents=[image_prompt, image_gen, scoring_prompt],
)
session_service = InMemorySessionService()

session = session_service.create_session(app_name="imagegen_news", 
                                        user_id='user1', 
                                        session_id='session11')
root_agent = llm_auditor
app = AdkApp(agent=root_agent, artifact_service_builder= InMemoryArtifactService())
