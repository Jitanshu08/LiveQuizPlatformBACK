from pydantic import BaseModel
from typing import List, Dict

class Participant(BaseModel):
    id: str
    score: int = 0

class QuizState(BaseModel):
    room: str
    current_question: dict = None
    participants: Dict[str, Participant] = {}
