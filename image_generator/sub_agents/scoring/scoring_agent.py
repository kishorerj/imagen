from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.models import LlmResponse

from google.adk.agents import LoopAgent
import os, json
import markdown2
from xhtml2pdf import pisa
import io

client = genai.Client(api_key='AIzaSyD50Se1v7ANmi_1AjYXdkjxcg4K616lLtw')
# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the policy file
policy_file_path = os.path.join(script_dir, 'policy.json')

def get_image(tool_context: ToolContext, counter: int) -> bytes:
  artifact  = tool_context.load_artifact(str(counter)+"_generated_image.png")
 
 
  if artifact and artifact.inline_data and artifact.inline_data.data:
      
      # The image is loaded into the context by load_artifact.
      # We just need to return a JSON-serializable confirmation.
      print(f"Successfully loaded artifact: generated_image.png")

      # Option 1: Simple confirmation (Recommended)
      return {'status': 'success', 'message': 'Image artifact 1_generated_image.png successfully loaded.'}

      # Option 2: Return base64 encoded string (if needed elsewhere, but usually not for the LLM)
      # image_bytes = artifact.inline_data.data
      # base64_image = base64.b64encode(image_bytes).decode('utf-8')
      # return {'status': 'success', 'image_base64': base64_image} # Still JSON serializable

  else:
      print(f"Failed to load artifact or artifact has no inline data")
      return {'status': 'error', 'message': f'Could not load image artifact  or it was empty.'}


    


def get_rules() -> str:
  """Loads the scoring policy from policy.json and returns it as a string."""
  try:
    with open(policy_file_path, 'r', encoding='utf-8') as f:
      # Read the entire file content as a string
      rules_string = f.read()
     
      return {'rules':  rules_string}
  except FileNotFoundError:
    print(f"Error: policy.json not found at {policy_file_path}")
    # Return an empty JSON object string or raise an error if the file is critical
    return "{}"
  except Exception as e:
    print(f"An unexpected error occurred while reading policy.json: {e}")
    return "{}"

def convert_to_pdf(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    print(llm_response)
    """Converts markdown text to PDF and returns the PDF as bytes."""
    # html_text = markdown2.markdown(llm_response.output)
    # pdf_buffer = io.BytesIO() # creates a buffer that allows the pdf to be saved in memory
    # pisa_status = pisa.CreatePDF(html_text, dest=pdf_buffer)
    # if pisa_status.err:
    #     raise Exception(f"Error creating PDF: {pisa_status.err}")
    # pdf_buffer.seek(0) # important that the seek is set to the beginning so we can read the file
    # pdf_buffer.read() # reads bytes from the buffer to be downloaded
    return llm_response
  
scoring_images_prompt = Agent(
    name="scoring_images_prompt",
    model="gemini-1.5-pro",
    description=(
        "You are an expert in evaluating and scoring images based on various criteria provided to you"
    ),
    instruction=(
        # 1. Instruct the LLM to get the image first
        "First, invoke the 'get_rules' tool to obtain the 'rules' in JSON format. "
        # 2. Instruct the LLM to get the rules
        "Next, invoke the 'get_image' tool to load the images artifact. Do not try to generate the image, just invoke the get_image function to get the image." 
        "Pass the counter variable as 1 during first invocation, 2 during second invocation and so on."
        # 3. Instruct the LLM to perform the scoring using the loaded image and rules
        "Now,  the image made available by the 'get_image' tool and the rules from 'get_rules', "
        "score  the image based on its compliance with each rule criterion. "
        "Evaluate the image against each criterion mentioned in the JSON string. "
        "Assign a score of 5 if the image complies with a specific criterion, else assign a score of 1. "
        "Do not validate the JSON structure itself; only use its content for scoring rules. "
        # 4. Specify the output format
        "OUTPUT: The output must be strictly in Markdown table format. It should have three columns: "
        "'Scoring Criteria', 'Score', and 'Reason' (explaining why a specific score was assigned)."
    ),
    output_key="result",
    tools=[get_rules, get_image],
    after_model_callback=convert_to_pdf
)

loop_scoring_images_prompt = LoopAgent(
    name="loop_scoring_images_prompt",
    max_iterations=3,
    sub_agents=[scoring_images_prompt]


)
    