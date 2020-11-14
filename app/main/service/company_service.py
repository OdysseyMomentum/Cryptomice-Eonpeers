import datetime
import uuid

from app.main.model.company import Company
from app.main.model.location import Location
from app.main.services import db
from app.main.util.tasks import validate_new_company
from app.main.util.eonerror import EonError
from app.main.util.keymanagementutils import KeyManagementClient


def save_new_company(data):
    company = Company.query.filter_by(vat_number=data['vat_number']).first()
    if not company:

        new_company = Company(
            public_id=str(uuid.uuid4()),
            name=data['name'],
            vat_number=data['vat_number'],
            created_on=datetime.datetime.utcnow(),
            is_own=False,
            base_url=data['base_url'],
            public_key=data.get('public_key', None)
        )
        save_changes(new_company) 

        #GET data from the new base_url and check if it matches
        if(data['base_url']):
            base_url = data['base_url'] if data['base_url'][-1]=='/' else data['base_url']+'/'
            _task = validate_new_company.delay(base_url+'company/node-owner', new_company.public_id)
            #validate_new_company(base_url+'company/node-owner', new_company.public_id)

        return generate_creation_ok_message(new_company)
    else:
       raise EonError('Another company already exists with the given data.', 409)


def get_all_companies():
    return Company.query.filter_by(is_own=False).all()

def get_node_owner():
    """ 
    Gets the details of the company owning the node, 

    Passed to the DTO in the controller, only meraningful fields are put in the response.
    Notice that the key is retrieved via KMC, so it's returned in bytes and thus decoded.

    """
    owner = Company.query.filter_by(is_own=True).first()
    kmc = KeyManagementClient()
    owner.public_key = kmc.get_serialized_pub_key().decode('utf-8')
    return owner

def get_a_company(public_id):
    return Company.query.filter_by(public_id=public_id).first()

def get_locations_of_a_company(company_id):
    return Location.query.filter_by(company_id=company_id).all()


def save_changes(data):
    db.session.add(data)
    db.session.commit()


def generate_creation_ok_message(company):
    try:
        response_object = {
            'status': 'success',
            'message': 'New company created and currently being checked.',
            'public_id': company.public_id
        }
        return response_object, 201
    except Exception:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 401
