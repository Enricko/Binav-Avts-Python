from app import create_app, socketio

app = create_app()

socketio.run(app, debug=True)
app.app_context().push()


# d: & cd python/binav avts python & .\env\scripts\activate & python main.py