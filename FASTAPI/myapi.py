from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai.OpenRouter_service import call_openrouter
router = APIRouter()

class ChatRequest(BaseModel):
    message : str
    image : str = ""

class ChatResponse(BaseModel):
    reply : str

@router.post("/chat",response_model = ChatResponse)
async def chat(request:ChatRequest):
    #validate input
    if not request.message.strip():
        raise HTTPException(status_code=400,detail="message can not be impty")
    try:
        reply = await call_openrouter(request.message, request.image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"internal error: {str(e)}")
    if reply is None:
        reply = "no response from ai"
    return ChatResponse(reply=reply.strip())








