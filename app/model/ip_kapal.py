from app.extensions import db

class IpKapal(db.Model):
    __tablename__ = "ip_kapals"

    id_ip_kapal = db.Column(db.Integer, primary_key=True)
    call_sign = db.Column(
        db.String(255),
        db.ForeignKey("kapals.call_sign", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    type_ip = db.Column(db.Enum("all", "gga", "hdt", "vtg"), nullable=False)
    ip = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    kapal = db.relationship("Kapal", backref="ip_kapals", lazy=True)

    def __repr__(self):
        return f"<IpKapal(id_ip_kapal={self.id_ip_kapal}, call_sign={self.call_sign}, type_ip={self.type_ip}, ip={self.ip}, port={self.port}, timestamps={self.timestamps})>"

