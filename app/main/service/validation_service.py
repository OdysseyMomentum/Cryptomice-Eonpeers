import datetime
import uuid

from app.main.model.validation import Validation
from app.main.model.location import Location
from app.main.model.company import Company
from app.main.services import db
from app.main.service.location_service import save_new_external_location
from app.main.util.tasks import validate_remote_location
from app.main.util.eonerror import EonError
from app.main.util.keymanagementutils import KeyManagementClient
from app.main.util.hashutils import HashUtils


def create_new_validation(data):
    """
    Create the requested validation object, connected to the proper company and location

    the data payload contains everything about the location but expectes the company to be already there,
    so the requesting party should make sure the company gossiping is finished before requesting validations.
    The inbound payload contains the location data and the requesting company public_key. 
    The payload is manipulated to reflect the expected payload for creating a new location.

    Final note: for now you can create more validations for the same locations, TBD

    Parameters
    ----------
    data: dict
        the incomin payload of the POST request with the following keys:
        'company_public_key', the public key of the requesting company
        'location_name'
        'location_data'
        'location_key'

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
        409, the given location already exists with the same key
    """
    #escaped_key = data['company_public_key'].replace('\n','\\n')
    requesting_company = Company.query.filter_by(public_key=data['company_public_key']).first()   
    if not requesting_company or not requesting_company.public_key:
        raise EonError('Unknown or incomplete company, craete the company first.', 400)
    existing_location = Location.query.filter_by(location_key=data['location_key']).first()
    location_id = ''
    if not existing_location:
        trascoded_payload = data
        trascoded_payload['name'] = data['location_name']
        trascoded_payload['company_id'] = requesting_company.public_id
        #save_new_external_location raises EonError if there are problems with the data
        location_id = save_new_external_location(trascoded_payload)[0]['public_id']
    else:
        location_id = existing_location.public_id
    #create the validation in a pending state
    new_validation = Validation(
        public_id=str(uuid.uuid4()),
        created_on=datetime.datetime.utcnow(),
        location_id=location_id
    )
    save_changes(new_validation) 
    return generate_creation_ok_message(new_validation)

def sign_a_validation(public_id):
    """
    Sign the given validation with the local key, must be protected by admin_token

    Parameters
    ----------
    public_id: str
        the id on the local db of the validaiton to sign

    Returns
    -------
    dict
        the validaiton object with the signed field filled

    Raises
    ------
    EonError
        500: when the signature breaks it raises Exception

    """
    validation = Validation.query.filter_by(public_id=public_id).first()
    if not validation:
        raise EonError('Validation does not exist.', 404)
    location = Location.query.filter_by(public_id=validation.location_id).first()
    try:
        hu = HashUtils()
        kmc = KeyManagementClient()
        payload_to_sign = location.name+location.location_key
        hashed_payload = hu.digest(payload_to_sign)
        signed_validation = kmc.sign_message(hashed_payload) #hexdigest this?
        validation.signed_location_key = signed_validation['signed'].hex()
        signer_company = Company.query.filter_by(is_own = True).first()
        #TODO: check integrity, the public key of the KMC must match the public key expected by the requesting party
        validation.signer_company_id = signer_company.public_id
        save_changes(validation)
        validation = Validation.query.filter_by(public_id=public_id).first()
        #launch a job that notifies the requestor:
        _task = validate_remote_location.delay(location.public_id, validation.public_id)

        return generate_signed_ok_message(validation)
    except Exception as e:
        print(e)
        raise EonError('Something is wrong with the signature system', 500) 

def receive_a_validation(data):
    """
    This is the service that the signer calls once he's done with the signature

    Retrieve the local location and company by theri keys that are passed in the request body
    retrieve or create the validation local object and add the data.
    Link the singing and requesting companies to the correct companies 
    so that base_urls can be retrieved (e.g. to check the validation on the signing node)
    
    Parameters
    ----------
    data: dict
        the payload of the request
        'location_key': the key (hash of location data) - hex string
        'signed_location_key': signed key (signed name + hash)
        'signer_public_key': pub_key of the signer
        'signer_validation_id': validation_id on the signer node

    Returns
    -------
    dict
        response message
        'status'
        'message'

    Raises
    ------
    EonError
        500: when the signature is corrupt

    """
    location = Location.query.filter_by(location_key=data['location_key']).first()
    signer_key = data['signer_public_key']
    signer_company = Company.query.filter_by(public_key=signer_key).first()   
    if not signer_company or not signer_company.public_key:
        raise EonError('Unknown or incomplete company, craete the company first.', 400)
    #TODO: check the signature
    new_validation = Validation(
        public_id=str(uuid.uuid4()),
        created_on=datetime.datetime.utcnow(),
        location_id=location.public_id,
        signer_company_id = signer_company.public_id,
        signed_location_key = data['signed_location_key']
    )
    save_changes(new_validation) 
    return generate_creation_ok_message(new_validation)

def get_a_validation(public_id):
    return Validation.query.filter_by(public_id=public_id).first()

def get_validations_by_location_id(location_id):
    return Validation.query.filter_by(location_id=location_id).all()

def save_changes(data):
    db.session.add(data)
    db.session.commit()

def generate_creation_ok_message(validation):
    try:
        response_object = {
            'status': 'success',
            'message': 'New validation created.',
            'public_id': validation.public_id
        }
        return response_object, 201
    except Exception:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 401

def generate_signed_ok_message(validation):
    try:
        response_object = {
            'status': 'success',
            'message': 'Validation signed.',
            'public_id': validation.public_id
        }
        return response_object, 204
    except Exception:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 401
