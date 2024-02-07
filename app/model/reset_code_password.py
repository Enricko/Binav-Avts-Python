from app.extensions import db


class ResetCodePassword(db.Model):
    __tablename__ = "reset_code_passwords"

    email = db.Column(db.String(255), primary_key=True, index=True)
    code = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<ResetCodePassword(email={self.email}, code={self.code}, timestamps={self.timestamps})>"
