import atexit
import threading
from app import check_for_new_configurations, create_app, socketio,scheduler

app = create_app()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    config_thread = threading.Thread(target=check_for_new_configurations)
    config_thread.start()
    socketio.run(app, debug=True)

# d: & cd python/binav avts python & .\env\scripts\activate & python main.py