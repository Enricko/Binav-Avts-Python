from app.extensions import db

class CoordinateHDT(db.Model):
    __tablename__ = "coordinate_hdts"

    id_coor_hdt = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(255), nullable=False)
    call_sign = db.Column(
        db.String(255),
        db.ForeignKey("kapals.call_sign", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    heading_degree = db.Column(db.Float, nullable=False)
    checksum = db.Column(db.String(255), nullable=False)
    timestamps = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False
    )

    kapal = db.relationship("Kapal", backref="coordinate_hdts", lazy=True)

    def __repr__(self):
        return f"<CoordinateHDT(id_coor_hdt={self.id_coor_hdt}, message_id={self.message_id}, call_sign={self.call_sign}, heading_degree={self.heading_degree}, timestamps={self.timestamps})>"
