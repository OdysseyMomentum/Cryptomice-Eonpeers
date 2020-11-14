import datetime

from app.main.config import key
from app.main.services import db, flask_bcrypt


class Validation(db.Model):
    """ Validation Model for storing validation related details """
    __tablename__ = "validation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100), unique=True, index=True)
    created_on = db.Column(db.DateTime, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=True)
    signed_location_key = db.Column(db.String(255), unique=True, nullable=True)
    signer_validation_id = db.Column(db.String(255), unique=False, nullable=True)
    signer_company_id = db.Column(db.String(100), db.ForeignKey('company.public_id'), nullable=True)
    location_id = db.Column(db.String(100), db.ForeignKey('location.public_id'), nullable=False)

    @property
    def status(self):
        if not self.signed_location_key:
            return 'pending'
        else:
            return 'signed'

    def __repr__(self):
        return "<Validation from company '{}' of location '{}'>".format(self.company_id, self.location_id)

    