from fastapi import APIRouter,HTTPException, UploadFile,File
from pydantic import BaseModel  
import uuid
import os
import base64
import json
from ai.OpenRouter_service import call_openrouter
router = APIRouter()

class ImageResponse(BaseModel) :
    monument : str
    confidence : float

@router.post("/analyze_image",response_model=ImageResponse) 
async def analyze_image(file: UploadFile = File(...) ): 
    allowed_MIME_types = ["image/jpeg", "image/png","image/jpg", "image/jfif", "image/gif"] 
    if file.content_type not in allowed_MIME_types:
        raise HTTPException(status_code=415,detail="Unsupported file type")
   
    try:
        contents = await file.read()
        encode_image = base64.b64encode(contents).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"failed to read image: {e}")
    
    prompt = ("You are an expert in monument recognition. Look at the image and identify the monument."
    "Return **only** a valid JSON object with exactly two keys:"
    "'monument'(a string) and 'confidence' (a float between 0.0 and 10)"
    "Do not iclude any other text, explanations, markdowns, backticks, or code fences"
    "Example: {\"monument\": \"Kremlin\"}, \"confidence\": 0,9")
    result_text = await call_openrouter(prompt,encode_image, file.content_type) 
    try:
        result_text = await call_openrouter(prompt, encode_image, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Ai service error: {e}")
    monument = "unkwon monument"
    confidence = 0.7 
        
    try : 
      cleaned = result_text.strip()
      if cleaned.startswith("```json"):
          cleaned = cleaned[7:]
      if cleaned.endswith("```"):
          cleaned = cleaned[-3:]
      cleaned = cleaned.strip()
      data = json.loads(cleaned)
      monument = data.get("monument", monument)
      
      confidence = float(data.get("confidence", confidence))
      
           
    except (json.JSONDecodeError, ValueError, TypeError) as e :
            print(f"JSON parsing failed: {e}, raw response: {result_text}")
            
             
    confidence = max(0.0, min(1.0, confidence))
    return ImageResponse(monument=monument, confidence=confidence)
