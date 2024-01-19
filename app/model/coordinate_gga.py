from app.extensions import db

class CoordinateGGA(db.Model):
    __tablename__ = "coordinate_ggas"

    id_coor_gga = db.Column(db.Integer, primary_key=True)
    call_sign = db.Column(
        db.String(255),
        db.ForeignKey("kapals.call_sign", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    message_id = db.Column(db.String(255), nullable=False)
    utc_position = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    direction_latitude = db.Column(db.String(1), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    direction_longitude = db.Column(db.String(1), nullable=False)
    gps_quality_indicator = db.Column(
        db.Enum(
            "Fix not valid",
            "GPS fix",
            "Differential GPS fix (DGNSS), SBAS, OmniSTAR VBS, Beacon, RTX in GVBS mode",
            "Not applicable",
            "RTK Fixed, xFill",
            "RTK Float, OmniSTAR XP/HP, Location RTK, RTX",
            "INS Dead reckoning",
        ),
        nullable=False,
    )
    number_sv = db.Column(db.Integer, nullable=False)
    hdop = db.Column(db.Float, nullable=False)
    orthometric_height = db.Column(db.Float, nullable=False)
    unit_measure = db.Column(db.String(255), nullable=False)
    geoid_separation = db.Column(db.Float, nullable=False)
    geoid_measure = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    kapal = db.relationship("Kapal", backref="coordinate_ggas", lazy=True)

    def __repr__(self):
        return f"<CoordinateGGA(id_coor_gga={self.id_coor_gga}, call_sign={self.call_sign}, message_id={self.message_id}, utc_position={self.utc_position}, latitude={self.latitude}, longitude={self.longitude}, timestamps={self.timestamps})>"

