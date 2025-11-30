import gradio as gr
import requests
import logging
from config import Settings # <--- Ensure you have a 'config.py' file

# --- Configuration & Setup ---

# Set up logging for better visibility of API calls and errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the API URL from settings
try:
    API_URL = f"{Settings.MCP_CLIENT_BASE_URL}/api/v1/agent/offline_agent"
    logging.info(f"API endpoint set to: {API_URL}")
except AttributeError:
    # Handle case where Settings or the URL key is missing
    logging.error("Configuration Error: Settings or MCP_CLIENT_BASE_URL not found. Using local placeholder URL.")
    # IMPORTANT: Replace this with your actual local/remote server address if needed
    API_URL = "http://127.0.0.1:5353/api/v1/agent/offline_agent" 


# --- Agent Communication Function ---

def chat_with_agent(message, history):
    """
    Sends the user message and conversation history to the backend API.

    :param message: The latest user input string.
    :param history: The list of previous conversation turns 
                    ([[user_msg_1, bot_resp_1], ...]) provided by gr.ChatInterface.
    :return: The agent's response string.
    """
    if not message:
        return "Please enter a message to begin the chat."
    
    # Prepare the payload for the backend API
    payload = {
        "prompt": message,
        # The history from Gradio is usually in the correct format for agent backends
        "history": history 
    }
    
    agent_reply = "⚠️ No response from agent" # Default safety message

    try:
        logging.info(f"Sending request for message: '{message}'")
        
        # Make the POST request with a reasonable timeout
        response = requests.post(API_URL, json=payload, timeout=600)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status() 

        # Parse JSON response and extract the reply
        data = response.json()
        
        # Safely extract the 'response' key, assuming the backend returns {'response': '...'}
        agent_reply = data.get("response", "⚠️ Agent replied, but the expected 'response' key was missing in the JSON.")
        logging.info("Successfully received reply from agent.")

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        agent_reply = f"❌ HTTP Error {status_code}: Could not reach backend agent."
        logging.error(f"HTTP Error: {status_code} - {e}")
        
    except requests.exceptions.RequestException as e:
        agent_reply = f"❌ Connection Error: Request failed (Timeout or Connection Refused). Details: {e}"
        logging.error(f"Request Error: {e}")
        
    except Exception as e:
        agent_reply = f"❌ General Error: An unexpected error occurred. Details: {e}"
        logging.error(f"General Error: {e}")

    # Return the agent's reply. gr.ChatInterface handles display and history update.
    return agent_reply


# --- Gradio Interface ---

# Use gr.ChatInterface for the cleanest implementation
iface = gr.ChatInterface(
    fn=chat_with_agent,
    title="🤖 Test Data Offline Agent",
    # description="Chat with your AI agent connected to MongoDB.",
    # Component customization
    chatbot=gr.Chatbot(height=500), # Defines the display window
    textbox=gr.Textbox(placeholder="Ask your MongoDB questions and press Enter or the Send button...", lines=2),
    # The Send/Submit button is automatically included by gr.ChatInterface
    theme=gr.themes.Soft(), # Optional theme customization
)

# Launch the application
iface.launch(server_name="0.0.0.0", server_port=7860)