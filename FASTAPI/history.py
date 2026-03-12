from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai.OpenRouter_service import call_openrouter

router = APIRouter()

class HistoryRequest (BaseModel):
    monument_name : str

class HistoryResponse (BaseModel):
    monument : str
    HistoricalInformation : str

@router.post("/history", response_model=HistoryResponse)
async def history(data: HistoryRequest) :
 try:
    if not data.monument_name.strip():
        raise HTTPException(status_code=400,detail = "The monument name is required")
    prompt = f"""You are an expert tour guide. Provide a concise but informative historical overview of {data.monument_name}. Include the following details if available:
     -When it was built and by whom
     -Its original purpose and significance
     -Key historical events associated with it
     -Its architectural style
     -Its current status(e.g: UNESCO World Heratige site, Tourist attraction)
      Write it clear. Don't use markdown, bullet points, or numbered lists. Just plain text."""
    result = await call_openrouter(prompt)
    if result.startswith(('API error", "Connection error')):
        raise HTTPException(status_code=500, detail= f"AI service error: {result}")
    
    return  HistoryResponse(monument = data.monument_name, HistoricalInformation = result.strip())
 except Exception as e:

    print(f"History endpoint error: {repr(e)}")
    raise HTTPException(status_code=500, detail="internal server error")

