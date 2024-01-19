from app.extensions import db

class Coordinate(db.Model):
    __tablename__ = "coordinates"

    id_coor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    call_sign = db.Column(
        db.String(255),
        db.ForeignKey("kapals.call_sign", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    series_id = db.Column(db.BigInteger, nullable=False)
    id_coor_gga = db.Column(
        db.Integer,
        db.ForeignKey(
            "coordinate_ggas.id_coor_gga", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=True,
    )
    id_coor_hdt = db.Column(
        db.Integer,
        db.ForeignKey(
            "coordinate_hdts.id_coor_hdt", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=True,
    )
    id_coor_vtg = db.Column(
        db.Integer,
        db.ForeignKey(
            "coordinate_vtgs.id_coor_vtg", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=True,
    )
    default_heading = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    kapal = db.relationship("Kapal", backref="coordinates", lazy=True)
    coordinate_gga = db.relationship("CoordinateGGA", backref="coordinates", lazy=True)
    coordinate_hdt = db.relationship("CoordinateHDT", backref="coordinates", lazy=True)
    coordinate_vtg = db.relationship("CoordinateVTG", backref="coordinates", lazy=True)

    def __repr__(self):
        return f"<Coordinate(id_coor={self.id_coor}, call_sign={self.call_sign}, series_id={self.series_id}, default_heading={self.default_heading}, timestamps={self.timestamps})>"
