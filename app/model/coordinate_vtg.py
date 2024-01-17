from app.extensions import db

class CoordinateVTG(db.Model):
    __tablename__ = "coordinate_vtgs"

    id_coor_vtg = db.Column(db.Integer, primary_key=True)
    call_sign = db.Column(
        db.String(255),
        db.ForeignKey("kapals.call_sign", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    track_degree_true = db.Column(db.Float, nullable=False)
    true_north = db.Column(db.String(1), nullable=False)
    track_degree_magnetic = db.Column(db.Float, nullable=False)
    magnetic_north = db.Column(db.String(1), nullable=False)
    speed_in_knots = db.Column(db.Float, nullable=False)
    measured_knots = db.Column(db.String(1), nullable=False)
    kph = db.Column(db.Float, nullable=False)
    measured_kph = db.Column(db.String(1), nullable=False)
    mode_indicator = db.Column(
        db.Enum(
            "Autonomous mode",
            "Differential mode",
            "Estimated (dead reckoning) mode",
            "Manual Input mode",
            "Simulator mode",
            "Data not valid",
        ),
        nullable=False,
    )
    checksum = db.Column(db.String(255), nullable=False)
    timestamps = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False
    )

    kapal = db.relationship("Kapal", backref="coordinate_vtgs", lazy=True)

    def __repr__(self):
        return f"<CoordinateVTG(id_coor_vtg={self.id_coor_vtg}, call_sign={self.call_sign}, track_degree_true={self.track_degree_true}, speed_in_knots={self.speed_in_knots}, timestamps={self.timestamps})>"

