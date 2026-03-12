import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json, uuid
from ai.OpenRouter_service import call_openrouter

router = APIRouter()
sessions : Dict[str, Dict[int, int]]={}

class GenRequest(BaseModel):
    monument : str
    num : int = 5

class Question(BaseModel):
    id : int
    question : str
    options : list[str]

class GenResponse(BaseModel):
    quiz_id : str
    questions : list[Question]

class AnswerItem(BaseModel):
    qid : int
    selected : int 

class SubmitRequest(BaseModel):
    quiz_id : str
    answers : list[AnswerItem]

class SubmitResponse(BaseModel):
    score : int
    total : int
    

async def generate_questions(monument : str, n : int) -> list[Dict[str, Any]]:
    prompt = f"""Genrate {n} MCQs about {monument}. You must output **only** a raw json array. No explinations, no markdown, no backticks.
    The array must contain objects with exactly these fields:
       
    -  "q": "string (the question)",
    -  "options": array of 4 strings, each starting with "A) ", "B) ", "C) ", "D) "
    -  "correct": 0 //index of the correct option (0-based)
    Example valid response :
    [{{"q": "Who built Taj Mahal?", "options": ["A) Shah Jahan", "B) Akbar", "C) Babur", "D) Aurangzeb], "correct": 0}}]
    Begin your response with '['and end with ']'. Do not include any additional text or explination."""
    response = await call_openrouter(prompt, "")

    print("===RAW RESPONSE===")
    print(repr(response))
    print("==================") 
    try:
        return json.loads(response)
    except json.JSONDecodeError:

     start= response.find('[') 
     end= response.rfind(']')+1
     if start==-1 or end==0: 
        raise ValueError("Invalid AI response")
    json_str = response [start:end]
    json_str = json_str.lstrip('\ufeff')

    print("===EXTRACTED JSON===")
    print(repr(json_str))
    print("====================")
    
    return json.loads(json_str)
   


@router.post("/generate", response_model = GenResponse)
async def generate_quiz(data : GenRequest):
    if not data.monument.strip():
        raise HTTPException(400, "Monument can not be empty")
    if not (1 <= data.num <=10):
        raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 10")
    try:
        raw_questions = await generate_questions(data.monument, data.num)
    except Exception as e:
        raise HTTPException(500, f"generation failed: {str(e)}")    
    quiz_id = str(uuid.uuid4())
    questions_list = []
    correct_map = {}
    for idx, q_data in enumerate(raw_questions):
        if not all(k in q_data for k in ("q", "options", "correct")):
            raise HTTPException(status_code=500, detail="AI response missing required fields")
        questions_list.append(Question(
                id=idx,
                question=q_data["q"],
                options=q_data["options"]
            )
        )
        correct_map[idx] = q_data["correct"]

    sessions[quiz_id] = correct_map
    return GenResponse(quiz_id=quiz_id, questions=questions_list)    
    

@router.post("/Submit",response_model = SubmitResponse)
async def Submit(data : SubmitRequest):
    correct_map = sessions.get(data.quiz_id)
    if not correct_map: raise HTTPException(404, "Quiz not found")
    score = 0
    for answers in data.answers:
        if correct_map.get(answers.qid) == answers.selected:
            score+=1
            return SubmitResponse(score=score, total=len(data.answers))

     



