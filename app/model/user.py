import re
from app.extensions import db
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id_user = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    email_verified_at = db.Column(db.TIMESTAMP, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    password_string = db.Column(db.String(255), nullable=False)
    level = db.Column(db.Enum("client", "admin", "owner"), nullable=False)
    remember_token = db.Column(db.String(100), nullable=True)
    timestamps = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False
    )

    @validates("email")
    def validate_email(self, key, email):
        if not email:
            raise AssertionError("Email field is required")
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id_user != self.id_user:
            raise AssertionError("Email already exists")
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            raise AssertionError("Please provide a valid email address")
        return email

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise AssertionError("Name field is required")
        return name

    @validates("level")
    def validate_level(self, key, level):
        if not level:
            raise AssertionError("Level field is required")
        if level not in ["client", "admin", "owner"]:
            raise AssertionError("Invalid level value")
        return level

    def set_password(self, password,password_confirmation):
        if not password:
            raise AssertionError("Password field is required")
        if len(password) < 8 or len(password) > 50:
            raise AssertionError("Password must contain at least 8")
        if password != password_confirmation:
            raise AssertionError("Password confirmation doesnt match")
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User(id_user={self.id_user}, name={self.name}, email={self.email}, level={self.level})>"