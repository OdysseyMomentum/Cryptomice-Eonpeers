from flask_restplus import Namespace, fields


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'email': fields.String(required=True,
                               description='user email address'),
        'username': fields.String(required=True, description='user username'),
        'public_id': fields.String(description='user Identifier')
    })
    new_user = api.model('new_user', {
        'email': fields.String(required=True,
                               description='user email address'),
        'username': fields.String(required=True, description='user username'),
        'password': fields.String(required=True, description='user password')
    })


class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True,
                                  description='The user password'),
    })


class CompanyDto:
    api = Namespace('company', description='company related operations')
    company = api.model('company', {
        'public_id': fields.String(description='company local Identifier'),
        'name': fields.String(required=True,
                              description='company name'),
        'vat_number': fields.String(required=True,
                                description='company identificaiton number'),
        'base_url': fields.String(required=True,
                                description='base url of the node controlled by the company'),
        'public_key': fields.String(required=False,
                                description='base url of the node controlled by the company')
    })
    new_company = api.model('new_company', {
        'name': fields.String(required=True,
                              description='company name'),
        'vat_number': fields.String(required=True,
                                description='company identificaiton number'),
        'base_url': fields.String(required=True,
                                description='base url of the node controlled by the company'),
        'public_key': fields.String(required=False,
                                description='base url of the node controlled by the company')
    })
    node_owner_company = api.model('node_owner_company', {
        'public_id': fields.String(description='company local Identifier'),
        'name': fields.String(required=True,
                              description='company name'),
        'vat_number': fields.String(required=True,
                                description='company identificaiton number'),
        'base_url': fields.String(required=True,
                                description='base url of the node controlled by the company'),
        'public_key': fields.String(required=True,
                                description='base url of the node controlled by the company')
    })

class LocationDto:
    api = Namespace('location', description='location related operations')
    location = api.model('location', {
        'public_id': fields.String(description='location local identifier'),
        'name': fields.String(required=True,
                              description='location name'),
        'location_data': fields.String(required=True,
                                description='data describing the location'),
        'location_key': fields.String(required=False,
                                description='the hash of location_data signed by the connected company'),
        'company_id': fields.String(required=True,
                                description='the public id of the connected company')
    })
    new_location = api.model('new_location', {
        'name': fields.String(required=True,
                              description='company name'),
        'location_data': fields.String(required=True,
                                description='data describing the location'),
        'company_id': fields.String(required=True,
                                description='the public id of the connected company')
    })

class ValidationDto:
    api = Namespace('validation', description='validation related operations')
    validation = api.model('validation', {
        'public_id': fields.String(description='validation local identifier'),
        'created_on': fields.Date(description='Date when the validation was created in pending status'),
        'status': fields.String(required=True,
                                description='status of the validation: pending/signed'),
        'signed_location_key': fields.String(required=False,
                                description='signature of approval by the local company'),
        'signer_company_id': fields.String(required=True,
                                description='the local public id of the company who signed the location key'),
        'location_id': fields.String(required=True,
                                description='the public id of the location')
    })
    new_validation_request = api.model('new_validation_request', {
        'location_name': fields.String(required=True,
                              description='name for the location to be created (if not already present) and validated'),
        'location_data': fields.String(required=True,
                                description='data describing the location'),
        'location_key': fields.String(required=False,
                                description='the hash of location_data signed by the requesting company'),
        'company_public_key': fields.String(required=True,
                                description='the public key of the company requesting the validation')
    }) 
    validation_to_sign = api.model('validation_to_sign', {
        'public_id': fields.String(description='validation local identifier'),
        'location_id': fields.String(required=True,
                                description='the local public id of the location')
    })
    new_validation = api.model('new_validation', {
        'signer_validation_id': fields.String(required=True,
                              description='public_id on the validating company node of the validation'),
        'signed_location_key': fields.String(required=True,
                                description='The signed version of the name+location key by the validating company'),
        'location_key': fields.String(required=True,
                                description='the hash of location_data signed by the requesting company'),
        'signer_public_key': fields.String(required=True,
                                description='the public key of the company signing the validation')
    }) 

class PositionDto:
    api = Namespace('position', description='position related operations')
    position = api.model('position', {
        'public_id': fields.String(required=True, description='public identifier of this object on this node'),
        'hash_id': fields.String(required=True, description='public identifier of this object in the network'),
        'signed_hash': fields.String(required=False, description='hash_id signed by the related company owner'),
        'created_on': fields.Date(required=True, description='creation date of the shipment within this node'),
        'company_id': fields.String(required=True, description='the local public id of the company who holds this position'),
        'shipment_id': fields.String(required=True, description='the local public id of the shipment the position refers to'),
        'position': fields.Integer(required=True, description='index of the posistion in handling the shipment'),
        'role': fields.String(required=True, description='description of the role held in the position (e.g. 1,brandowner; 2,producer; .. ')
    })
    new_position = api.model('new_position', {
        'company_id': fields.String(required=True, description='the local public id of the company who holds this position'),
        'shipment_id': fields.String(required=True, description='the local public id of the shipment the position refers to'),
        'position': fields.Integer(required=True, description='index of the posistion in handling the shipment'),
        'role': fields.String(required=True, description='description of the role held in the position (e.g. 1,brandowner; 2,producer; .. ')
    })
    import_position = api.model('import_position', {
        'company_vat': fields.String(required=True, description='the local public id of the company who holds this position'),
        'position': fields.Integer(required=True, description='index of the posistion in handling the shipment'),
        'role': fields.String(required=True, description='description of the role held in the position (e.g. 1,brandowner; 2,producer; .. '),
        'hash_id':fields.String(required=True, description='the public id of the position in the network'),
        'signed_hash':fields.String(required=False, nullable=True, description='the hash_id signed by the respective company'),
    })
    position_to_sign = api.model('position_to_sign', {
        'public_id': fields.String(description='position local identifier')
    })

class ShipmentDto:
    api = Namespace('shipment', description='shipment related operations')
    shipment = api.model('shipment', {
        'public_id': fields.String(required=True, description='public identifier of this object on this node'),
        'hash_id': fields.String(required=True, description='public identifier of this object in the network'),
        'name': fields.String(required=True,
                                description='reference name for this shipment'),
        'created_on': fields.Date(required=True,
                                description='creation date of the shipment within this node'),
        'shipment_date': fields.Date(required=True,
                                description='creation date of the shipment within this node'),
        'origin': fields.String(required=True, description='origin location'),
        'destination': fields.String(required=True, description='destination location'),
        'hs_code': fields.String(required=True, description='type of goods classification code'),
        'description': fields.String(required=True, description='description'),
        'current_company_id': fields.String(required=True, description='the local public id of the company who is the current holder'),
        'waybill_number': fields.String(required=True, description='reference number of the waybill'),
        'custom_reference_number': fields.String(required=True, description='the identifier of this shipment put into a custom reference field or other service info field')
    })
    new_shipment = api.model('new_shipment', {
        'name': fields.String(required=True,
                                description='reference name for this shipment'),
        'shipment_date': fields.Date(required=True,
                                description='creation date of the shipment within this node'),
        'origin': fields.String(required=True, description='origin location'),
        'destination': fields.String(required=True, description='destination location'),
        'hs_code': fields.String(required=True, description='type of goods classification code'),
        'description': fields.String(required=True, description='description'),
        'current_company_id': fields.String(required=True, description='the local public id of the company who is the current holder'),
        'waybill_number': fields.String(required=True, description='reference number of the waybill'),
        'custom_reference_number': fields.String(required=True, description='the identifier of this shipment put into a custom reference field or other service info field')
    })
    import_shipment = api.model('import_shipment', {
        'hash_id': fields.String(required=True, description='public identifier of this object in the network'),
        'name': fields.String(required=True,
                                description='reference name for this shipment'),
        'shipment_date': fields.Date(required=True,
                                description='creation date of the shipment within this node'),
        'origin': fields.String(required=True, description='origin location'),
        'destination': fields.String(required=True, description='destination location'),
        'hs_code': fields.String(required=True, description='type of goods classification code'),
        'description': fields.String(required=True, description='description'),
        'current_company_vat': fields.String(required=True, description='the vat of the company which is the current holder'),
        'waybill_number': fields.String(required=True, description='reference number of the waybill'),
        'custom_reference_number': fields.String(required=True, description='the identifier of this shipment put into a custom reference field or other service info field'),
        'positions':fields.List(fields.Nested(PositionDto.import_position))
    })


class MethodResultDto:
    api = Namespace('method_result', description='special methods rpc-like')
    method_result = api.model('method_result', {
        'method': fields.String(required=True, description='The called method'),
        'result': fields.String(required=True, description='The result'),
    })
