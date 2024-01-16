from dotenv import load_dotenv
from flask import Flask, jsonify
from app.routes import bp as main_bp
from database.database import db
from config.app import api

load_dotenv()

app = Flask(__name__)

db.init_app(app)
api.init_app(app)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
