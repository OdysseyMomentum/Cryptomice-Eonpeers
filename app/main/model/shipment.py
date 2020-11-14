import datetime

from app.main.config import key
from app.main.services import db, flask_bcrypt


class Shipment(db.Model):
    """ Location Model for storing location related details """
    __tablename__ = "shipment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100), unique=True, index=True)
    hash_id = db.Column(db.String(100), unique=True, index=True)
    name = db.Column(db.String(255), unique=False, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    shipment_date = db.Column(db.DateTime, nullable=True)
    origin = db.Column(db.String(255), unique=False, nullable=False)
    destination = db.Column(db.String(255), unique=False, nullable=False)
    hs_code = db.Column(db.String(255), unique=False, nullable=True)
    description = db.Column(db.String(255), unique=False, nullable=True)
    serials_hash = db.Column(db.String(255), unique=False, nullable=True)
    current_company_id = db.Column(db.String(100), db.ForeignKey('company.public_id'))
    waybill_number = db.Column(db.String(255), unique=False, nullable=True)
    custom_reference_number = db.Column(db.String(255), unique=False, nullable=True)

    
    def __repr__(self):
        return "<Origin '{}', destination '{}', created_on '{}'>".format(self.origin, self.destination, self.created_on)
