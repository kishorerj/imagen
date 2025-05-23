
import os, config
from google import genai


# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the policy file
policy_file_path = os.path.join(script_dir, 'orig_policy.json')


client = genai.Client()
  



def convert_policy_to_text():
    # Read policy file
    try:
        with open(policy_file_path, 'r', encoding='utf-8') as f:
            policy_string = f.read()
    except FileNotFoundError:
        print(f"Error: policy.json not found at {policy_file_path}")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading policy.json: {e}")
        return

    # Create prompt
    prompt = f"""
Convert Policy JSON to text description so that I can pass this to an LLM as a part of its input prompt. 
---
Policy:
{policy_string}
---
Instructions:
    - Output Format: JSON (Like Python Dictionary)
    - The key of the output will be the entities ("Interested Entities" as is when provided) and the value will be its summary in plain text from guidelines section. 
    - Interested Entities is optional. If it is not provided, then consider that everything provided within the context of guidelines is important and needed. In this case, you are free to assume the keys in output. 
    - DO IT CAREFULLY: If "Interested Entities" not provided, you are free to club common entities under one banner and remove redundancy. Combine its value properly. 
    - Note: If "Interested Entities" are present and there is global/common information available in the guidelines which is applicable to all entities, please add that information within the current entity values. 
    - The output JSON depth should only be 1, as-in, it should not be multi-nested structure.
"""

    # Call Gemini model
    response = client.models.generate_content(model=config.GENAI_MODEL, contents=prompt)

    policy_text = response.text

    # Save response to file
    with open('policy.json', 'w', encoding='utf-8') as f:
        f.write(policy_text)
    print(f"Policy saved to policy.json")

    return policy_text


if __name__ == "__main__":
    convert_policy_to_text()
  