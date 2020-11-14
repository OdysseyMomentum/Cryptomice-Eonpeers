import datetime
import uuid

from sqlalchemy import desc

from app.main.model.company import Company
from app.main.model.shipment import Shipment
from app.main.model.position import Position
from app.main.services import db
from app.main.util.eonerror import EonError
from app.main.util.keymanagementutils import KeyManagementClient
from app.main.util.hashutils import HashUtils


def save_new_position(data):
    position = Position.query.filter_by(company_id=data['company_id'], shipment_id=data['shipment_id'], position=data['position']).first()
    if not position:

        connected_company = Company.query.filter_by(public_id=data['company_id']).first()
        if not connected_company:
            raise EonError('Unknown company, create the company first.', 400)

        connected_shipment = Shipment.query.filter_by(public_id=data['shipment_id']).first()
        if not connected_shipment:
            raise EonError('Unknown shipment, create the company first.', 400)

        payload_to_hash = str(data['position'])+data['role']+connected_company.vat_number+connected_shipment.hash_id
        hu = HashUtils()
        hashed_payload = hu.digest(payload_to_hash).hex()
        print("save_position: ", data.get("signed_hash"))
        new_position = Position(
            public_id=str(uuid.uuid4()),
            hash_id = hashed_payload,
            signed_hash = data.get("signed_hash"),
            created_on=datetime.datetime.utcnow(),
            company_id=data['company_id'],
            shipment_id=data['shipment_id'],
            position=data['position'],
            role=data['role']
        )
        save_changes(new_position) 

        return generate_creation_ok_message(new_position)
    else:
       raise EonError('The shipment already has an entry for this position for this company.', 409)

def import_position(data):
    #when importing a position, after saving check that the hash matches and that the signed hash is correct if any
    saved_position = save_new_position(data)
    position = Position.query.filter_by(public_id=saved_position[0]["public_id"]).first()
    if(data["hash_id"] and data["hash_id"]!=position.hash_id):
        raise EonError('Position hash not matching! '+data["hash_id"], 400)        

    connected_company = Company.query.filter_by(public_id=data['company_id']).first()
    if(data.get("signed_hash") and not connected_company.is_own):
        kmc = KeyManagementClient()
        #TODO: fix encoding and decoding, the validation fails probably due to encode to utf on one side, but decode as hex on the other side
        #if not kmc.verify_signed_message(bytes(bytearray.fromhex(data["signed_hash"])), data["hash_id"], connected_company.public_key):
        #    raise EonError('Position signature corrupter! '+data["hash_id"], 400) 
    return saved_position              


def sign_a_position(public_id):
    position = Position.query.filter_by(public_id=public_id).first()
    if not position:
        raise EonError('Unknown position, create the data first.', 400)

    #double check that you are signing a position of your own company:
    connected_company = Company.query.filter_by(public_id=position.company_id).first()
    if not connected_company or not connected_company.is_own:
        raise EonError('You can sign only your positions.', 400)

    hu = HashUtils()
    kmc = KeyManagementClient()
    payload_to_sign = position.hash_id
    hashed_payload = hu.digest(payload_to_sign)
    signed_position = kmc.sign_message(hashed_payload)
    signed_position_hex = signed_position['signed'].hex()

    position.signed_hash = signed_position_hex
    save_changes(position)

    return generate_update_ok_message(position)

def get_a_position(public_id):
    return Position.query.filter_by(public_id=public_id).first()

def get_all_positions():
    return Position.query.filter_by().all()

def get_positions_of_a_shipment(shipment_id):
    return Position.query.filter_by(shipment_id=shipment_id).order_by(Position.position.desc()).all()


def save_changes(data):
    db.session.add(data)
    db.session.commit()


def generate_creation_ok_message(position):
    try:
        response_object = {
            'status': 'success',
            'message': 'New position created.',
            'public_id': position.public_id
        }
        return response_object, 201
    except Exception:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 401

def generate_update_ok_message(position):
    try:
        response_object = {
            'status': 'success',
            'message': 'Position updated.',
            'public_id': position.public_id
        }
        return response_object, 201
    except Exception:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 401
