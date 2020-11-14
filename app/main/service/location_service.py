import datetime
import uuid

from app.main.model.location import Location
from app.main.model.company import Company
from app.main.services import db
from app.main.util.tasks import make_gossip_call
from app.main.util.eonerror import EonError
from app.main.util.keymanagementutils import KeyManagementClient
from app.main.util.hashutils import HashUtils


def save_new_location(data):
    """
    Save a new location for your owned company, i.e. sign the location_key with your key
    """
    location = Location.query.filter_by(company_id=data['company_id'], name=data['name']).first()
    if not location:
        #get the key of the connected company, if "is_own", call the keymanagement system:
        connected_company = Company.query.filter_by(public_id=data['company_id']).first()
        if not connected_company:
            raise EonError('Unknown company, craete the company first.', 400)

        key = ''
        kmc = KeyManagementClient()
        hu = HashUtils()
        if connected_company.is_own and connected_company.public_key==None:
            #use the KMC to retrieve the public key and then sign the hash of the location_data
            hashed_location_data = hu.digest(data['location_data'])
            key = kmc.sign_message(hashed_location_data) #hexdigest this?
        else:
            raise EonError('The company does not have a known public key.', 400)

        new_location = Location(
            public_id=str(uuid.uuid4()),
            name=data['name'],
            location_data=data['location_data'],
            created_on=datetime.datetime.utcnow(),
            company_id = data['company_id'],
            location_key=key['signed'].hex()
        )
        save_changes(new_location) 

        return generate_creation_ok_message(new_location)
    else:
       raise EonError('Another location already exists with the given data.', 409)

def save_new_external_location(data):
    """
    Save a new location from another company, check the signature. The payload has the key because you can't compute it

    This funciton is called from the POST new validation, so the request body is manipulated to find the proper
    parameters, e.g. the validation request has the company public key, not the company_id as we need to insert into DB

    Parameters
    ----------
    data: dict
        the body of the request with the following keys;
        'name', name of the location
        'location_key', the signed key for the location
        'location_data', the payload describing the location
        'company_id', the id of the connected company

    Returns
    -------
    dict
        the body of the response, a dict witht he following keys:
        'status',
        'message',
        'public_id', the local public_id for this location

    Raises
    ------
    EonError
        400, something is wrong witht the input data
        409, the given company already has a location with the same key
    """
    location = Location.query.filter_by(company_id=data['company_id'], location_key=data['location_key']).first()
    if not location:
        connected_company = Company.query.filter_by(public_id=data['company_id']).first()
        if not connected_company:
            raise EonError('Unknown company, craete the company first.', 400)

        if connected_company.public_key and not connected_company.is_own:
            public_key = connected_company.public_key
            hu = HashUtils()
            kmc = KeyManagementClient()
            hashed_location_data = hu.digest(data['location_data'])
            bytes_key = bytes.fromhex(data['location_key'])
            signature_correct = kmc.verify_signed_message(bytes_key, hashed_location_data, public_key)
            if not signature_correct:
                raise EonError('Invalid signature for the given location.', 400)
        else:
            raise EonError('The company does not have a known public key.', 400)
        #TODO:
        #check the company public key by retrieving it
        new_location = Location(
            public_id=str(uuid.uuid4()),
            name=data['name'],
            location_data=data['location_data'],
            created_on=datetime.datetime.utcnow(),
            company_id = data['company_id'],
            location_key=data['location_key']
        )
        save_changes(new_location) 
        return generate_creation_ok_message(new_location)
    else:
        raise EonError('Another location already exists with the given data.', 409)

def get_a_location(public_id):
    return Location.query.filter_by(public_id=public_id).first()

def save_changes(data):
    db.session.add(data)
    db.session.commit()

def generate_creation_ok_message(location):
    try:
        response_object = {
            'status': 'success',
            'message': 'New location created and currently being checked.',
            'public_id': location.public_id
        }
        return response_object, 201
    except Exception:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 401
