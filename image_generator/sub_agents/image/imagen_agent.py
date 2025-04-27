from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from google.adk.agents import Agent
from google.adk.tools import ToolContext 
import os,uuid,tempfile

image_uris=[]
client = genai.Client(api_key='AIzaSyD50Se1v7ANmi_1AjYXdkjxcg4K616lLtw')
def generate_images(prompt: str, counter: int, tool_context: ToolContext):

    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images= 1
        )
        
    )
    generated_image_paths = [] 
    for generated_image in response.generated_images:
            # Get the image bytes
            image_bytes = generated_image.image.image_bytes  
            report_artifact = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/png"
            
            )      
            tool_context.save_artifact(str(counter)+"_generated_image.png", report_artifact)

image_generation_agent = Agent(
    name="image_generation_agent",
    model="gemini-2.0-flash",
    description=(
        "You are an expert in creating images with imagen 3"
    ),
    instruction=(
        "Invoke the 'generate_images' tool by passing the prompt in the 'imagen_prompts' variable as the prompt." \
     
        "You should invoke the 'generate_images' tool once for each prompt. Pass the counter variable as 1 during first" \
        "invocation, 2 during second invocation and so on" \
    
    ),
    tools=[generate_images],
    output_key="output_image"
)
  