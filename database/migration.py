from flask import Flask
from database.database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost/python_db'
# Replace 'username', 'password', 'localhost', and 'dbname' with your MySQL credentials and database name

db.init_app(app)

with app.app_context():
    db.create_all()
