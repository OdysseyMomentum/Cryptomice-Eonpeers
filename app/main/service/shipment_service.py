import datetime
import uuid

from app.main.model.shipment import Shipment
from app.main.model.position import Position
from app.main.model.company import Company
from app.main.services import db
from app.main.service.position_service import import_position, sign_a_position
from app.main.util.tasks import send_shipment
from app.main.util.eonerror import EonError
from app.main.util.keymanagementutils import KeyManagementClient
from app.main.util.hashutils import HashUtils


def save_new_shipment(data):
    shipment = Shipment.query.filter_by(name=data['name']).first()
    if not shipment:

        connected_company = Company.query.filter_by(public_id=data['current_company_id']).first()
        if not connected_company:
            raise EonError('Unknown company, create the company first.', 400)

        #you create the hash with the now() timestamp only as a shipment creator, other peers import the hash
        hashed_payload =  data["hash_id"]
        now = datetime.datetime.utcnow()
        if not data["hash_id"]:
            payload_to_hash = data["name"]+now.isoformat()+data["shipment_date"]+data["origin"]+data["destination"]+data["hs_code"]+data["description"]
            hu = HashUtils()
            hashed_payload = hu.digest(payload_to_hash).hex()

        new_shipment = Shipment(
            public_id=str(uuid.uuid4()),
            hash_id=hashed_payload,
            name=data['name'],
            created_on=now,
            shipment_date=datetime.datetime.fromisoformat(data["shipment_date"]),
            origin=data['origin'],
            destination=data['destination'],
            hs_code=data.get('hs_code', None),
            description=data.get('description', None),
            current_company_id=data['current_company_id'],
            waybill_number=data.get('waybill_number', None),
            custom_reference_number=data.get('custom_reference_number', None)
        )
        save_changes(new_shipment) 

        return generate_creation_ok_message(new_shipment)
    else: 
       raise EonError('Another shipment already exists with the given data.', 409)

def get_all_shipments():
    return Shipment.query.filter_by().all()

def get_a_shipment(public_id):
    return Shipment.query.filter_by(public_id=public_id).first()

def get_shipments_of_a_company(company_id):
    return Shipment.query.filter_by(company_id=company_id).all()

def get_positions_of_a_shipment(shipment_id):
    return Position.query.filter_by(shipment_id=shipment_id).all()

def send_shipment_to_next_peer(shipment_id):
    """
    send the shipment to the next peer, which will add its info and return it back
    """
    payloads = prepare_shipment_payload(shipment_id)
    #pyalkods[0]: JSON payload to send, [1]: next position
    if not payloads[1] and payloads[0]:
        raise EonError('Missing company or shipment, create the data first.', 400)

    _task = send_shipment.delay(payloads[0], payloads[1])

def receive_shipment_from_previous_peer(data):
    """
    receive a shipment payload, check for matching data and create it
    """
    current_company = Company.query.filter_by(vat_number=data["current_company_vat"]).first()
    if not current_company:
        raise EonError('Missing company, create the company first.', 400)

    #add the missing keys to insert the shipment:
    data["current_company_id"] = current_company.public_id

    #check if you already have this shipment
    erxisting_shipment = Shipment.query.filter_by(hash_id=data["hash_id"]).first()
    if(erxisting_shipment):
        #TODO: if you have, the sender should use a different call, to update the shipment position, not to create a new one
        raise EonError('A shipment with this hash already exist.', 404)

    new_shipment_result = save_new_shipment(data)[0]
    if not new_shipment_result["public_id"]:
        raise EonError('Error while creating the new shipment.', 500)

    #create the positions
    if not data["positions"] or len(data["positions"])<2:
        raise EonError('Missing or corrupt positions data.', 400)

    for position in data["positions"]:
        position_company = Company.query.filter_by(vat_number=position["company_vat"]).first()
        if not position_company:
            print("gossip to get this company info ", position["company_vat"])
        position_payload = {
            "position":position["position"],
            "role":position["role"],
            "hash_id":position["hash_id"],
            "signed_hash":position.get("signed_hash"),
            "company_id":position_company.public_id,
            "shipment_id":new_shipment_result["public_id"]
        }
        saved_position = import_position(position_payload)


def prepare_shipment_payload(shipment_id):
    """
    prepare the payload to describe the shipment for the next party

    In current_position there the position of the company giving currently holding the shipment
    in next_position there's the expected position of the next company, which will receive the payload
    """
    #get the shipment and the connected positions
    #in the payload company reference must be vats, shipment reference the hash of its fields
    shipment = Shipment.query.filter_by(public_id=shipment_id).first()
    if not shipment:
        raise EonError('Missing shipment or wrong id.', 400)
    company = Company.query.filter_by(public_id = shipment.current_company_id).first()
    if not company:
        raise EonError('Missing company or wrong id.', 400)
    positions = Position.query.filter_by(shipment_id=shipment_id).order_by(Position.position.asc()).all()
    positions_array = []
    target_company = ""
    for position in positions:
        #sign position of the current company, if it's not already signed
        pos_company = Company.query.filter_by(public_id = position.company_id).first()
        if(pos_company.is_own and not position.signed_hash):
            sign_a_position(position.public_id)
            position = Position.query.filter_by(public_id=position.public_id).first()
        position_payload = {
            "company_vat":pos_company.vat_number,
            "position":position.position,
            "role":position.role,
            "hash_id":position.hash_id,
            "signed_hash": position.signed_hash if position.signed_hash else ""
        }
        target_company = position.company_id
        positions_array.append(position_payload)

    if not positions_array or len(positions_array)<2:
        raise EonError('Missing positions, create at least the current and next one.', 400)

    #check that the last position needs to be sent and was not already sent
    payload = {   
        'hash_id':shipment.hash_id,     
        'name':shipment.name,
        'shipment_date':shipment.shipment_date.isoformat(),
        'origin':shipment.origin,
        'destination':shipment.destination,
        'hs_code':shipment.hs_code,
        'description':shipment.description,
        'current_company_vat':company.vat_number,
        'waybill_number':shipment.waybill_number,
        'custom_reference_number':shipment.custom_reference_number,
        'positions': positions_array
    }
    return payload, target_company

def save_changes(data):
    db.session.add(data)
    db.session.commit()


def generate_creation_ok_message(shipment):
    try:
        response_object = {
            'status': 'success',
            'message': 'New shipment created and currently being checked.',
            'public_id': shipment.public_id
        }
        return response_object, 201
    except Exception:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 401
