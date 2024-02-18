import atexit
from app import create_app, socketio,scheduler

app = create_app()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    socketio.run(app, debug=True)

# d: & cd python/binav avts python & .\env\scripts\activate & python main.py