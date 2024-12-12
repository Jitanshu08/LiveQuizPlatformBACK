from fastapi import APIRouter
from utils.ai import generate_questions
from websocket.quiz_ws import websocket_handler
from pydantic import BaseModel

class QuestionRequest(BaseModel):
    topic: str

class StartQuizRequest(BaseModel):
    room: str
    questions: list

class JoinRoomRequest(BaseModel):
    room: str
    sid: str

class SubmitAnswerRequest(BaseModel):
    room: str
    sid: str
    answer: str

quiz_router = APIRouter()

@quiz_router.post("/start")
async def start_quiz(request: StartQuizRequest):
    room = request.room
    questions = request.questions

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
async def join_room(request: JoinRoomRequest):
    room = request.room
    sid = request.sid
    await websocket_handler.join_room(room, sid)
    return {"message": "Joined room"}

@quiz_router.post("/submit-answer")
async def submit_answer(request: SubmitAnswerRequest):
    room = request.room
    sid = request.sid
    answer = request.answer
    await websocket_handler.submit_answer(room, sid, answer)
    return {"message": "Answer submitted"}