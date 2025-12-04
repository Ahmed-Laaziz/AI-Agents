import gradio as gr
import requests
import logging
from config import Settings

# --- Configuration & Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define Endpoints
OFFLINE_AGENT_URL = f"{Settings.MCP_CLIENT_BASE_URL}/api/v1/agent/offline_agent"
WORKFLOW_URL = f"{Settings.MCP_CLIENT_BASE_URL}/api/v1/agent/workflow" # Matches your router

# Default fallback for testing if config fails
if not Settings.MCP_CLIENT_BASE_URL:
    OFFLINE_AGENT_URL = "http://127.0.0.1:5353/api/v1/agent/offline_agent"
    WORKFLOW_URL = "http://127.0.0.1:5353/api/v1/agent/workflow"

# --- Logic Functions ---

def chat_with_agent(message, history):
    """
    Handles 'Free Conversation' mode via /offline_agent
    """
    if not message:
        return ""

    payload = {
        "prompt": message,
    }

    try:
        response = requests.post(OFFLINE_AGENT_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "⚠️ Response missing 'response' key.")
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_workflow(model_name):
    """
    Handles 'Predefined Workflow' mode via /workflow
    Returns the agent's text output directly.
    """
    
    payload = {
        "prompt": "Trigger Workflow", 
        "model": model_name
    }
    
    try:
        status_msg = f"🚀 Workflow triggered for model **{model_name}**... Please wait (this may take a moment)."
        
        response = requests.post(WORKFLOW_URL, json=payload, timeout=300) 
        response.raise_for_status()
        
        # --- KEY CHANGE: Parse JSON and strip surrounding quotes/newlines ---
        
        # 1. Attempt to parse as JSON first. 
        # Even if the backend only returned the string "Based on...", requests might treat it as 
        # a JSON string that needs to be decoded.
        try:
            # If the backend returned a JSON string like '{"response": "..."}' or 
            # if FastAPI/requests wrapper puts the string in quotes, this extracts the content.
            agent_output_text = response.json() 
        except requests.exceptions.JSONDecodeError:
            # If it's pure raw text without outer quotes, use response.text
            agent_output_text = response.text
            
        # 2. Clean the string to remove any persistent outer quotes or whitespace.
        # This handles cases where the raw string starts/ends with a quote or a newline.
        if isinstance(agent_output_text, str):
            # Clean up leading/trailing quotes and whitespace
            # .strip() handles whitespace, and we explicitly remove quotes if present.
            final_output = agent_output_text.strip().strip('"')
        else:
            # Should not happen if the backend returns a string, but as a fallback
            final_output = str(agent_output_text)
            
        # 3. Ensure \n are correctly interpreted by Gradio's Markdown component
        # Gradio's Markdown component usually handles \n for line breaks correctly, 
        # but if it fails, you might need to replace \n with HTML <br> or double spaces/newlines
        # for strict Markdown compliance. However, usually, a clean string is enough.
        
        return final_output
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_details = e.response.text if e.response.text else "No further details."
        return f"❌ **Workflow HTTP Error {status_code}**: Could not reach backend agent.\nDetails: {error_details}"
        
    except Exception as e:
        return f"❌ **Workflow Failed**: An unexpected error occurred.\nDetails: {str(e)}"
def on_mode_select(choice):
    """
    Shows/Hides groups based on selection
    """
    if choice == "Free Conversation":
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)

# --- Main Application ---

with gr.Blocks(theme=gr.themes.Soft(), title="🤖 AI Orchestrator") as demo:
    
    gr.Markdown("# 🤖 Intelligent Agent System")
    
    # 1. Selection Area
    with gr.Row():
        mode_radio = gr.Radio(
            choices=["Free Conversation", "Predefined Workflow"],
            value="Free Conversation",
            label="Select Interaction Mode",
            info="Choose 'Free Conversation' to chat or 'Workflow' to run the automated analysis."
        )

    # 2. Free Conversation Interface (Chatbot)
    with gr.Group(visible=True) as chat_group:
        gr.Markdown("### 💬 Free Conversation")
        chatbot = gr.Chatbot(height=450)
        msg = gr.Textbox(placeholder="Ask me anything about the test data...", show_label=False)
        clear = gr.ClearButton([msg, chatbot])

        # Hook up ChatInterface logic manually using components
        msg.submit(
            fn=lambda m, h: (m, h + [[m, None]]), 
            inputs=[msg, chatbot], 
            outputs=[msg, chatbot], 
            queue=False
        ).then(
            fn=lambda m, h: h[-1].__setitem__(1, chat_with_agent(h[-1][0], h[:-1])) or h,
            inputs=[msg, chatbot],
            outputs=[chatbot]
        )

    # 3. Workflow Interface (UPDATED SECTION)
    with gr.Group(visible=False) as workflow_group:
        gr.Markdown("### ⚙️ Predefined Workflow: Asset Analysis")
        
        with gr.Row():
            model_input = gr.Dropdown(
                choices=["llama3.2"], 
                value="llama3.2", 
                label="Model Selection"
            )
            run_btn = gr.Button("▶️ Run Workflow", variant="primary")
        
        # --- KEY CHANGE: Use gr.Markdown for the output ---
        # Markdown component automatically renders **bold** and *italics*
        output_area = gr.Markdown(
            label="Workflow Output", 
            value="*Workflow results will appear here...*"
        ) 
        
        # Hook up button
        run_btn.click(
            fn=run_workflow,
            inputs=[model_input],
            outputs=[output_area]
        )

    # 4. Toggle Logic
    mode_radio.change(
        fn=on_mode_select,
        inputs=[mode_radio],
        outputs=[chat_group, workflow_group]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)