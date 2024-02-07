from app.extensions import db
from sqlalchemy.orm import validates


class Client(db.Model):
    __tablename__ = "clients"

    id_client = db.Column(db.String(255), primary_key=True)
    id_user = db.Column(
        db.String(255),
        db.ForeignKey("users.id_user", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    status = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    user = db.relationship("User", backref="client", lazy=False)

    @validates("status")
    def validate_status(self, key, status):
        if status is None:
            raise AssertionError("Status field is required")
        if str(status).lower() not in ["true", "false"]:
            raise AssertionError("Status only contain [true/false]")
        return status

    def __repr__(self):
        return f"<Client(id_client={self.id_client}, id_user={self.id_user}, status={self.status}, timestamps={self.timestamps})>"
