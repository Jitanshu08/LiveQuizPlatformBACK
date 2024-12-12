from fastapi import FastAPI
from fastapi_socketio import SocketManager
from routes.quiz import quiz_router
from routes.user import user_router
from websocket.quiz_ws import websocket_handler

app = FastAPI()

# Initialize Socket.IO
socket_manager = SocketManager(app, cors_allowed_origins=["*"])  # Allow connections from any origin
websocket_handler.init_socket_manager(socket_manager)

# Include API routes
app.include_router(quiz_router, prefix="/quiz")
app.include_router(user_router, prefix="/user")

@app.get("/")
def read_root():
    return {"message": "Live Quiz Backend is Running!"}
