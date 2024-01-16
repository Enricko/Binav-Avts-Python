from database.database import db
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
    timestamps = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False
    )

    user = db.relationship("User", backref="client", lazy=True)
    
    @validates("status")
    def validate_status(self, key, status):
        if status not in [0,1]:
            raise AssertionError("Invalid status value")
        return status

    def __repr__(self):
        return f"<Client(id_client={self.id_client}, id_user={self.id_user}, status={self.status}, timestamps={self.timestamps})>"

