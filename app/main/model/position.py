import datetime

from app.main.config import key
from app.main.services import db, flask_bcrypt


class Position(db.Model):
    """ Location Model for storing location related details """
    __tablename__ = "position"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100), unique=True, index=True)
    hash_id = db.Column(db.String(100), unique=True, index=True)
    signed_hash = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, nullable=False)
    company_id = db.Column(db.String(100), db.ForeignKey('company.public_id'), nullable=False)
    shipment_id = db.Column(db.String(100), db.ForeignKey('shipment.public_id'), nullable=False)
    position = db.Column(db.Integer, unique=False, nullable=False)
    role = db.Column(db.Integer, unique=False, nullable=False)
    __table_args__ = (db.UniqueConstraint('company_id', 'shipment_id', 'position', name='_company_shipment_position_uc'),)

    def __repr__(self):
        return "<Shipment '{}', company '{}', position '{}'>".format(self.shipment_id, self.company_id, self.position)

    

