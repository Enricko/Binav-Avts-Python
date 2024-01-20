from app import create_app, socketio

app = create_app()

socketio.run(app, debug=True)

# d: & cd python/binav avts python & .\env\scripts\activate & python main.py