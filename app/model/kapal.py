from app.extensions import db

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
    class_ = db.Column(
        db.String(255), nullable=False
    )  # 'class' is a reserved word, use 'class_'
    builder = db.Column(db.String(255), nullable=False)
    year_built = db.Column(
        db.String(4), nullable=False
    )  # Assuming the year is a 4-digit string
    size = db.Column(db.Enum("small", "medium", "large", "extra_large"), nullable=False)
    xml_file = db.Column(db.Text, nullable=False)
    timestamps = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False
    )

    client = db.relationship("Client", backref="kapals", lazy=True)

    def __repr__(self):
        return f"<Kapal(call_sign={self.call_sign}, id_client={self.id_client}, status={self.status}, flag={self.flag}, class_={self.class_}, builder={self.builder}, year_built={self.year_built}, size={self.size}, xml_file={self.xml_file}, timestamps={self.timestamps})>"

