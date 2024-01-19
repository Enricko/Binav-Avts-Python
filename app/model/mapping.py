from app.extensions import db


class Mapping(db.Model):
    __tablename__ = "mappings"

    id_mapping = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(
        db.String(255),
        db.ForeignKey("clients.id_client", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    name = db.Column(db.String(255), nullable=False)
    file = db.Column(db.Text, nullable=False)
    switch = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    client = db.relationship("Client", backref="mappings", lazy=True)

    def __repr__(self):
        return f"<Mapping(id_mapping={self.id_mapping}, id_client={self.id_client}, name={self.name}, switch={self.switch}, timestamps={self.timestamps})>"
