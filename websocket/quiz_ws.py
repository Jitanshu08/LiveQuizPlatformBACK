import asyncio
from fastapi_socketio import SocketManager

class QuizWebSocket:
    def __init__(self):
        self.socket_manager = None
        self.active_rooms = {}  # Tracks participants in each room
        self.quiz_states = {}   # Tracks the quiz state for each room

    def init_socket_manager(self, socket_manager: SocketManager):
        self.socket_manager = socket_manager

    async def start_question_timer(self, room: str, time_limit: int):
        await asyncio.sleep(time_limit)
        if room in self.quiz_states:
            await self.socket_manager.emit("time_up", {"message": "Time's up!"}, room=room)
            await self.move_to_next_question(room)

    async def move_to_next_question(self, room: str):
        if room in self.quiz_states:
            # Assuming questions are preloaded in quiz_states
            current_question = self.quiz_states[room].get("current_question_index", 0)
            questions = self.quiz_states[room].get("questions", [])
            
            if current_question + 1 < len(questions):
                # Move to the next question
                self.quiz_states[room]["current_question_index"] = current_question + 1
                next_question = questions[current_question + 1]
                await self.broadcast_question(room, next_question)
            else:
                # End the quiz
                await self.end_quiz(room)

    async def end_quiz(self, room: str):
        if room in self.quiz_states:
            leaderboard = [
                {"participant": sid, "score": data["score"]}
                for sid, data in self.quiz_states[room]["participants"].items()
            ]
            leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
            await self.socket_manager.emit("quiz_ended", {"leaderboard": leaderboard}, room=room)
            # Clean up room data
            del self.quiz_states[room]
            del self.active_rooms[room]

    async def join_room(self, room: str, sid: str):
        if room not in self.active_rooms:
            self.active_rooms[room] = []
            self.quiz_states[room] = {"current_question": None, "participants": {}}
        self.active_rooms[room].append(sid)
        self.quiz_states[room]["participants"][sid] = {"score": 0}
        await self.socket_manager.emit("room_joined", {"room": room}, room=sid)
        
        # Send current question to the new participant
        if room in self.quiz_states and self.quiz_states[room]["current_question"]:
            await self.socket_manager.emit(
                "new_question", self.quiz_states[room]["current_question"], room=sid
            )


    async def leave_room(self, room: str, sid: str):
        if room in self.active_rooms and sid in self.active_rooms[room]:
            self.active_rooms[room].remove(sid)
            del self.quiz_states[room]["participants"][sid]
        if not self.active_rooms[room]:
            del self.active_rooms[room]

    async def broadcast_question(self, room: str, question: dict, time_limit: int = 30):
        if room in self.quiz_states:
            self.quiz_states[room]["current_question"] = question
            await self.socket_manager.emit("new_question", question, room=room)
            # Start the timer
            asyncio.create_task(self.start_question_timer(room, time_limit))


    async def submit_answer(self, room: str, sid: str, answer: str):
        if room in self.quiz_states and sid in self.quiz_states[room]["participants"]:
            # Logic to check correctness of answer and update score
            participant = self.quiz_states[room]["participants"][sid]
            correct_answer = self.quiz_states[room]["current_question"]["answer"]
            if answer == correct_answer:
                participant["score"] += 10
            await self.broadcast_leaderboard(room)

    async def broadcast_leaderboard(self, room: str):
        if room in self.quiz_states:
            leaderboard = [
                {"participant": sid, "score": data["score"]}
                for sid, data in self.quiz_states[room]["participants"].items()
            ]
            leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
            await self.socket_manager.emit("leaderboard", {"leaderboard": leaderboard}, room=room)

# Create an instance of QuizWebSocket
websocket_handler = QuizWebSocket()