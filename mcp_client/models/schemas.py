from pydantic import BaseModel
from typing import Optional
from config import Settings
class PromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = "llama3"

class ChatRequest(BaseModel):
    user_message: str
    system_prompt: Optional[str] = "You are a helpful assistant"
    model: Optional[str] = "llama3:8b"
    request_timeout: Optional[float] = 420.0
