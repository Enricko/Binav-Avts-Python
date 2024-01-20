from flask_socketio import emit
from app.extensions import socketio
import datetime

def socketrun1second():
    print("asdasasd")
    emit("message",f"{datetime.datetime.now()}")

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on('message')
def handle_message(msg):
    emit('message', msg,broadcast=True)
    emit('message', msg+"asd",broadcast=False)