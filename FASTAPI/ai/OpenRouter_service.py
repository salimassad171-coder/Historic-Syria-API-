import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY") 
OPENROUTER_URL=("https://openrouter.ai/api/v1/chat/completions")
Model = "meta-llama/llama-4-maverick"

async def call_openrouter(prompt:str, base64_image: str = None, mime_type : str = "image/jpeg")->str:
    if base64_image is not None and not isinstance(base64_image, str):
        base64_image = str(base64_image) if base64_image else None
    print(f"Debug: prompt={prompt}, has_image={bool(base64_image and base64_image.strip())}")
    has_image = base64_image and base64_image.strip() !=""
    if not OPENROUTER_API_KEY:
        print("Debug: no api key")
        return "DeepSeek API key not configured"
    headers = {
        "Authorization":f"Bearer {OPENROUTER_API_KEY}",
        "Content-type":"application/json",
        "HTTP-Referer": "http://127.0.0.1:8000",
        "X-Title": "My API"
    }
    
    if has_image:
        data_url = f"data:{mime_type};base64,{base64_image}"
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": data_url}
        ]
    else :
        content = prompt
    payload = {
        "model" : Model,
        "messages" :[{"role": "user", "content" : content}],
        "max_tokens" : 400,
        "temperature" : 0.7
    }    
    try :
        async with httpx.AsyncClient(timeout=120.0) as Client:
            response = await Client.post(OPENROUTER_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            print(f"debug: reply: {reply}")
            return reply
    except httpx.HTTPStatusError as e :
        return f"API error: {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e :
        return f"connection error: {str(e)}"
    except (KeyError, IndexError) :
        return f"Unexpected response format: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"




