
+# News Article Image Generator ADK Project
+
+This project uses the Google Agent Development Kit (ADK) to create a system that generates relevant images for news articles. It leverages Gemini for understanding the article and generating prompts, and Imagen 3 for the actual image creation.
+
+## Overview
+
+The system consists of two main agents:
+1.  **Prompt Generation Agent (`sub_agents/prompt/prompt_agent.py`)**:
+    *   Takes a news article as input.
+    *   Uses a Generative AI model (configured via `GENAI_MODEL` in `config.py`) to understand the article.
+    *   Generates a descriptive prompt suitable for Imagen 3 to create a visually representative image for the article.
+2.  **Image Generation Agent (`sub_agents/image/imagen_agent.py`)**:
+    *   Receives the generated prompt.
+    *   Uses the Imagen 3 model (configured via `IMAGEN_MODEL` in `config.py`) to generate an image.
+    *   Optionally saves the generated image to a Google Cloud Storage (GCS) bucket.
+    *   Saves the image as an ADK artifact.
+
+## Directory Structure
+
+```
+image_generator/
+├── config.py               # Main configuration file
+├── .env                    # (Recommended) For environment variables
+├── sub_agents/
+│   ├── image/
+│   │   └── imagen_agent.py   # Agent for generating images
+│   └── prompt/
+│       └── prompt_agent.py # Agent for generating prompts
+├── app.py                  # (Assumed) Main ADK application file
+└── README.md               # This file
+```
+*(You might need to create an `app.py` or similar in the `image_generator/` directory to orchestrate these agents if you don't have one already)*
+
+## Configuration
+
+Configuration for the project is managed through `image_generator/config.py` and an optional `image_generator/.env` file for environment-specific settings.
+
+### `config.py`
+
+Located at `image_generator/config.py`, this file contains the core settings for the agents.
+
+```python
+import os
+from dotenv import load_dotenv
+
+load_dotenv() # Loads variables from .env
+
+# Google Cloud Storage bucket name for storing generated images.
+# Can be overridden by setting GCS_BUCKET_NAME in the .env file.
+# If not set (e.g., GCS_BUCKET_NAME = None or an empty string), GCS upload will be skipped.
+GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "default-bucket-if-not-set")
+
+# Score threshold (Purpose might be for future evaluation logic)
+SCORE_THRESHOLD = 30
+
+# Maximum iterations (Purpose might be for future iterative processes)
+MAX_ITERATIONS = 3
+
+# Imagen model to be used for image generation
+IMAGEN_MODEL = 'imagen-3.0-generate-002'
+
+# GenAI model (e.g., Gemini) to be used for prompt generation
+GENAI_MODEL = 'gemini-2.0-flash'
+```
+
+**Key Variables:**
+*   `GCS_BUCKET_NAME`: The name of the Google Cloud Storage bucket where generated images will be uploaded. If this is not set (i.e., `None` or an empty string), the GCS upload step in `sub_agents/image/imagen_agent.py` will be skipped.
+*   `SCORE_THRESHOLD`: Currently defined but not actively used in the provided agent code. Potentially for future features related to image scoring or selection.
+*   `MAX_ITERATIONS`: Similar to `SCORE_THRESHOLD`, defined for potential future use.
+*   `IMAGEN_MODEL`: Specifies the Imagen model version for generating images.
+*   `GENAI_MODEL`: Specifies the Gemini (or other GenAI) model for generating the image prompts.
+
+### `.env` File (Recommended)
+
+For sensitive information (like API keys, if any in the future) or environment-specific settings (like the `GCS_BUCKET_NAME`), it's highly recommended to use a `.env` file. This file should be placed in the `image_generator/` directory (same level as `config.py`) and **should not be committed to version control** (add `.env` to your `.gitignore` file).
+
+1.  **Create the `.env` file:**
+    In the `image_generator/` directory, create a file named `.env`.
+
+2.  **Add your configurations:**
+    ```env
+    # Example .env content
+    GCS_BUCKET_NAME="your-actual-gcs-bucket-name-here"
+    # GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json" # If using service account keys
+    ```
+    Replace `"your-actual-gcs-bucket-name-here"` with your GCS bucket name.
+
+The `config.py` file (with the suggested modification to use `python-dotenv`) will automatically load variables from the `.env` file, overriding any default values set directly in `config.py` if the variable exists in `.env`.
+
+## Prerequisites
+
+*   Python (3.8 or higher recommended)
+*   Google Cloud SDK: Installed and initialized.
+*   Google ADK: `pip install google-adk`
+*   Required Python libraries: `pip install google-generativeai google-cloud-storage python-dotenv Pillow`
+
+## Setup
+
+1.  **Clone the Repository** (if applicable) or ensure you have the project files.
+2.  **Navigate to the Project Directory**:
+    ```bash
+    cd /path/to/your/project/imagen2/imagen/image_generator
+    ```
+3.  **Create and Activate a Virtual Environment** (Recommended):
+    ```bash
+    python -m venv venv
+    source venv/bin/activate  # On Windows: venv\Scripts\activate
+    ```
+4.  **Install Dependencies**:
+    ```sh
+    pip install google-generativeai Pillow google-cloud-storage google-adk python-dotenv
+    ```
+5.  **Google Cloud Authentication**:
+    Ensure you are authenticated with Google Cloud and have the necessary permissions for Vertex AI (Imagen) and Google Cloud Storage.
+    ```bash
+    gcloud auth application-default login
+    ```
+    If you are using a specific project, make sure it's configured:
+    ```bash
+    gcloud config set project YOUR_PROJECT_ID
+    ```
+6.  **Configure `.env` File**:
+    Create or update the `.env` file in the `image_generator/` directory as described in the "Configuration" section, especially setting your `GCS_BUCKET_NAME`.
+
+## Running with ADK Web
+
+The ADK Web interface allows you to interact with your agents. You'll typically run `adk web` pointing to a Python file that defines your ADK Application, which orchestrates your agents.
+
+1.  **Create an Application File (e.g., `app.py`)**:
+    If you don't have one, you'll need a main Python script (e.g., `app.py` in the `image_generator/` directory) that defines your ADK `Application` and includes your agents (`image_generation_prompt_agent` from `sub_agents.prompt.prompt_agent` and `image_generation_agent` from `sub_agents.image.imagen_agent`). This file would look something like:
+    ```python
+    # image_generator/app.py
+    from google.adk import Application # Or from google.adk.orchestration import Application
+    from sub_agents.prompt.prompt_agent import image_generation_prompt_agent
+    from sub_agents.image.imagen_agent import image_generation_agent
+
+    # Define how agents are chained or used
+    # This is a simplified example; your orchestration might be more complex.
+    main_app = Application(
+        name="NewsImageGeneratorApplication",
+        description="Generates images for news articles.",
+        agents=[image_generation_prompt_agent, image_generation_agent] # Or a sequence/graph
+    )
+    ```
+    *(Note: The exact ADK `Application` setup might vary based on your ADK version and how you want to chain agents.)*
+
+2.  **Run ADK Web**:
+    From your terminal, while in the `image_generator/` directory (or ensuring paths are correct):
+    ```bash
+    adk web app.py
+    ```
+    (Replace `app.py` with the actual name of your main ADK application file.)
+
+3.  **Interact via the Web UI**:
+    Open the URL provided by `adk web` (usually `http://127.0.0.1:8000`) in your browser.
+    *   You should see your application or agents listed.
+    *   Select the appropriate agent or workflow.
+    *   Provide the required input (e.g., a news article text for the `image_generation_prompt_agent` if it's the entry point).
+    *   The agents will execute, and you should see the generated prompt, the final image (as an artifact), and GCS upload status messages in the logs or UI.
+
+## How it Works
+
+1.  The user provides a news article.
+2.  The `image_generation_prompt_agent` (from `sub_agents/prompt/prompt_agent.py`) processes the article and generates a suitable prompt for Imagen.
+3.  This prompt is passed to the `image_generation_agent` (from `sub_agents/image/imagen_agent.py`).
+4.  The `image_generation_agent` uses Imagen (via the `generate_images` tool) to generate an image based on the prompt.
+5.  If `GCS_BUCKET_NAME` is configured, the image is uploaded to the specified GCS bucket.
+6.  The image is saved as an ADK artifact, accessible through the ADK framework.
+7.  The status and any relevant URIs or artifact names are returned.
+
+---
+
+Remember to replace placeholder paths and names with your actual project details.
+```

This README provides a good starting point. You can expand it further with more specific details about your project's workflow, advanced configurations, or troubleshooting tips as it evolves.
