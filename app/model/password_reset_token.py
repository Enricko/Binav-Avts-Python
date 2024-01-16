from database.database import db


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    email = db.Column(db.String(255), primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=True)

    def __repr__(self):
        return f"<PasswordResetToken(email={self.email}, token={self.token}, created_at={self.created_at})>"

