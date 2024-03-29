from app.extensions import db
from sqlalchemy.orm import validates

from app.model.client import Client

class Kapal(db.Model):
    __tablename__ = "kapals"

    call_sign = db.Column(db.String(255), primary_key=True)
    id_client = db.Column(
        db.String(255),
        db.ForeignKey("clients.id_client", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    status = db.Column(db.Boolean, nullable=False)
    flag = db.Column(db.String(255), nullable=False)
    kelas = db.Column(
        db.String(255), nullable=False
    )
    builder = db.Column(db.String(255), nullable=False)
    heading_direction = db.Column(db.Integer, nullable=False)
    year_built = db.Column(
        db.String(4), nullable=False
    )  # Assuming the year is a 4-digit string
    size = db.Column(db.Enum("small", "medium", "large", "extra_large"), nullable=False)
    xml_file = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    client = db.relationship("Client", backref="kapals", lazy=False)
    
    @validates("call_sign")
    def validate_call_sign(self, key, call_sign):
        if not call_sign:
            raise AssertionError("call_sign field is required")
        existing_data = Kapal.query.filter_by(call_sign=call_sign).first()
        if existing_data and existing_data.call_sign != self.call_sign:
            raise AssertionError("call_sign already exists")
        return call_sign
    
    @validates("id_client")
    def validate_id_client(self,key,id_client):
        if not id_client:
            raise AssertionError("id_client field is required")
        existing_data = Client.query.filter_by(id_client=id_client).first()
        if existing_data is None:
            raise AssertionError("id_client doesn't exists")
        return id_client
        
    @validates("status")
    def validate_status(self, key, status):
        if status is None:
            raise AssertionError("Status field is required")
        if str(status).lower() not in ["true","false"]:
            raise AssertionError("Status only contain [true/false]")
        return status
    
    @validates("flag")
    def validate_flag(self, key, flag):
        if not flag:
            raise AssertionError("Flag field is required")
        return flag
    
    @validates("kelas")
    def validate_kelas(self, key, kelas):
        if not kelas:
            raise AssertionError("Kelas field is required")
        return kelas
    
    @validates("builder")
    def validate_builder(self, key, builder):
        if not builder:
            raise AssertionError("Builder field is required")
        return builder
    
    @validates("year_built")
    def validate_year_built(self, key, year_built):
        if not year_built:
            raise AssertionError("year_built field is required")
        return year_built

    @validates("heading_direction")
    def validate_heading_direction(self, key, heading_direction):
        if heading_direction < 0 and heading_direction > 360:
            raise AssertionError("heading_direction value must be between 0 and 360")
        if not heading_direction:
            raise AssertionError("heading_direction field is required")
        return heading_direction
    
    @validates("size")
    def validate_size(self, key, size):
        if not size:
            raise AssertionError("Size field is required")
        if size not in ["small", "medium", "large", "extra_large"]:
            raise AssertionError("Invalid size value")
        return size
    
    @validates("image")
    def validate_image(self, key, image):
        if not image:
            raise AssertionError("image field is required")
        return image

    def __repr__(self):
        return f"<Kapal(call_sign={self.call_sign}, id_client={self.id_client}, status={self.status}, flag={self.flag}, class_={self.class_}, builder={self.builder}, year_built={self.year_built}, heading_direction={self.heading_direction}, size={self.size}, xml_file={self.xml_file},image={self.image}, timestamps={self.timestamps})>"

