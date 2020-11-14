import datetime

from app.main.config import key
from app.main.services import db, flask_bcrypt


class Company(db.Model):
    """ Company Model for storing company related details """
    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100), unique=True, index=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    vat_number = db.Column(db.String(255), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    is_own = db.Column(db.Boolean, nullable=False, default=False)
    base_url = db.Column(db.String(50))
    eori_number = db.Column(db.String(255), unique=True, nullable=True)
    aeo_status = db.Column(db.String(255), unique=False, nullable=True)
    public_key = db.Column(db.String(100))

    
    def __repr__(self):
        return "<Company '{}', vat '{}'>".format(self.name, self.vat_number)

    