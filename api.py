from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage
import uvicorn
from backend_code.backend import workflow , thread_id

app = FastAPI(title="Chat API", version="1.0")

# Pydantic models
class ChatRequest(BaseModel):
    # thread_id: str
    message: str

class ChatResponse(BaseModel):
    # thread_id: str
    response: str


# API Routes
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_req: ChatRequest):
    """Send a message to the chat workflow and get a response."""
    # Build a HumanMessage
    user_message = HumanMessage(content=chat_req.message)

    # Invoke workflow with thread_id for checkpointing
    result = workflow.invoke({"messages": [user_message]}, config={"configurable": {"thread_id": thread_id}})

    # Extract the last AI response
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    if ai_messages:
        response_text = ai_messages[-1].content
    else:
        response_text = "No response generated."

    return ChatResponse(thread_id=thread_id, response=response_text)


@app.get("/")
async def root():
    return {"message": "Chat API is running!"}


# Run server (dev mode)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



