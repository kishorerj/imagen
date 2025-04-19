from google import genai
from google.genai import types


client = genai.Client(api_key='AIzaSyD50Se1v7ANmi_1AjYXdkjxcg4K616lLtw')

response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents='Why is the sky blue?'
)
print(response.text)
