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

client = genai.Client()
# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the policy file
policy_file_path = os.path.join(script_dir, 'policy.json')

def get_image(tool_context: ToolContext):
  artifact_name = f"generated_image_"+ str(tool_context.state.get('loop_iteration', 0)) + ".png"
  artifact  = tool_context.load_artifact(artifact_name)
  print(f' gcs image uri: {tool_context.state.get('generated_image_gcs_uri')}')
  metadata = {}
 
  if artifact and artifact.inline_data and artifact.inline_data.data:
      #open the image from image bytes with pillow
      image = Image.open(BytesIO(artifact.inline_data.data))

      #list all the image metadata attributes from image and assign it to variables
      metadata['size'] = image.size
      metadata['mode'] = image.mode
      metadata['format'] = image.format
      #metadata['info'] = str(image.info)
      

      # The image is loaded into the context by load_artifact.
      # We just need to return a JSON-serializable confirmation.
      print(f"Successfully loaded artifact: generated_image.png")

      # Option 1: Simple confirmation (Recommended)
      return {'status': 'success', 'message': 'Image artifact "1_generated_image.png" successfully loaded.',
              'image_metadata': metadata
             }


  else:
      print(f"Failed to load artifact or artifact has no inline data")
      return {'status': 'error', 'message': f'Could not load image artifact  or it was empty.'}


def get_rules(tool_context: ToolContext) -> str:
  """Loads the scoring policy from policy.json and returns it as a string."""
  try:
    with open(policy_file_path, 'r', encoding='utf-8') as f:
      # Read the entire file content as a string
      rules_string = f.read()
     
      return {'rules':  rules_string}
  except FileNotFoundError:

    print(f"Error: policy.json not found at {policy_file_path}")
    tool_context.actions.escalate(True)
    # Return an empty JSON object string or raise an error if the file is critical
    return "{}"
  except Exception as e:
    print(f"An unexpected error occurred while reading policy.json: {e}")
    tool_context.actions.escalate(True)
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

def set_score(tool_context: ToolContext, total_score: int) -> str:
   print(f'total scoreeee is {total_score}')
   tool_context.state['total_score'] = total_score

   
   
  
scoring_images_prompt = Agent(
    name="scoring_images_prompt",
    model="gemini-2.0-flash",
    description=(
        "You are an expert in evaluating and scoring images based on various criteria provided to you"
    ),
  instruction=(
      "Your task is to evaluate an image based on a set of scoring rules. Follow these steps precisely:"
        "1.  First, invoke the 'get_rules' tool to obtain the image scoring 'rules' in JSON format"
        "2.  Next, invoke the 'get_image' tool to load the images artifact and image_metadata. Do not try to generate the image"
        "3.  Carefully examine the rules in JSON string obtained in step 1. For EACH rule described within this JSON string:"
        "    a.  Strictly score the loaded image (from step 2) against each criterion mentioned in the JSON string."
        "    b.  Assign a score in a scale of 0 to 5: 5 points if the image complies with a specific criterion, or 0 point if it does not." \
             "Also specify the reason in a seperate attribute explaining the reason for assigning thew score"
        "Do not validate the JSON structure itself; only use its content for scoring rules. "
       
        "OUTPUT JSON FORMAT SPECIFICATION:\n"
        "The JSON object MUST have exactly two top-level keys:"
        "  - 'total_score': Iterate through each individual score element in the json and add those to arrive at total_score. "
        "  - 'scores': The existing rules json with a score attribute assigned to each rule and a reason attribute"
      ),
    output_key="scoring",
    tools=[get_rules, get_image, set_score],
    after_model_callback=convert_to_pdf
)

# loop_scoring_images_prompt = LoopAgent(
#     name="loop_scoring_images_prompt",
#     max_iterations=3,
#     sub_agents=[scoring_images_prompt]


# )
    