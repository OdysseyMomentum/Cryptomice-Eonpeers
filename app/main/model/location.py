import datetime

from app.main.config import key
from app.main.services import db, flask_bcrypt


class Location(db.Model):
    """ Location Model for storing location related details """
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100), unique=True, index=True)
    name = db.Column(db.String(255), unique=False, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    location_data = db.Column(db.String(255), unique=False, nullable=False)
    location_key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    company_id = db.Column(db.String(100), db.ForeignKey('company.public_id'))

    
    def __repr__(self):
        return "<Location '{}', data '{}', key '{}'>".format(self.name, self.location_data, self.location_key)

    