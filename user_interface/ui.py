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
        response = requests.post(OFFLINE_AGENT_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "⚠️ Response missing 'response' key.")
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_workflow(model_name):
    payload = {
        "prompt": "Trigger Workflow",
        "model": model_name
    }

    try:
        response = requests.post(WORKFLOW_URL, json=payload, timeout=300)
        response.raise_for_status()

        data = response.json()
        return data.get("final_answer", "⚠️ Aucun résultat renvoyé par le workflow.")

    except Exception as e:
        return f"❌ Workflow Failed: {str(e)}"
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
                choices=["mistral"], 
                value="mistral", 
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