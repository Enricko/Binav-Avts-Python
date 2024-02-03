from app.extensions import db
from sqlalchemy.orm import validates

from app.model.client import Client

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
    status = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    client = db.relationship("Client", backref="mappings", lazy=False)
    
    @validates("id_client")
    def validate_id_client(self,key,id_client):
        if not id_client:
            raise AssertionError("id_client field is required")
        existing_data = Client.query.filter_by(id_client=id_client).first()
        if existing_data is None:
            raise AssertionError("id_client doesn't exists")
        return id_client
    
    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise AssertionError("Name field is required")
        return name
    
    @validates("file")
    def validate_file(self, key, file):
        if not file:
            raise AssertionError("file field is required")
        return file

    def __repr__(self):
        return f"<Mapping(id_mapping={self.id_mapping}, id_client={self.id_client}, name={self.name}, switch={self.switch}, timestamps={self.timestamps})>"
