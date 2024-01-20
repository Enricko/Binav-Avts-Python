from app.extensions import socketio
import datetime

def socketrun1second():
    print("asdasasd")
    socketio.emit("message",f"{datetime.datetime.now()}")

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on('message')
def handle_message(msg):
    print('Message:', msg)
    socketio.emit('message', msg)