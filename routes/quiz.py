from fastapi import APIRouter, Depends
from utils.ai import generate_questions
from websocket.quiz_ws import websocket_handler
from pydantic import BaseModel

class QuestionRequest(BaseModel):
    topic: str

class StartQuizRequest(BaseModel):
    room: str

quiz_router = APIRouter()

@quiz_router.post("/start")
async def start_quiz(room: str, questions: list):
    if room in websocket_handler.quiz_states:
        return {"error": "Quiz already started in this room."}
    
    websocket_handler.quiz_states[room] = {
        "current_question_index": 0,
        "questions": questions,
        "participants": {}
    }
    await websocket_handler.broadcast_question(room, questions[0])  # Broadcast first question
    return {"status": "Quiz Started"}

@quiz_router.post("/generate-questions")
async def generate_questions_route(request: QuestionRequest):
    questions = await generate_questions(request.topic)
    return {"questions": questions}

@quiz_router.post("/join-room")
async def join_room(room: str, sid: str):
    await websocket_handler.join_room(room, sid)
    return {"message": "Joined room"}

@quiz_router.post("/submit-answer")
async def submit_answer(room: str, sid: str, answer: str):
    await websocket_handler.submit_answer(room, sid, answer)
    return {"message": "Answer submitted"}