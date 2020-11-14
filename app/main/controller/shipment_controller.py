from flask import request
from flask_restplus import Resource

from app.main.service.shipment_service import (get_a_shipment, get_all_shipments, save_new_shipment, get_positions_of_a_shipment, send_shipment_to_next_peer, receive_shipment_from_previous_peer)
from app.main.util.dto import ShipmentDto, PositionDto
from app.main.util.decorator import admin_token_required, token_required
from app.main.util.eonerror import EonError

api = ShipmentDto.api
_shipment = ShipmentDto.shipment
_new_shipment = ShipmentDto.new_shipment
_position = PositionDto.position
_import_shipment = ShipmentDto.import_shipment

parser = api.parser()
parser.add_argument('Authorization', location='headers', help="Auth token from login")

@api.route('/')
class ShipmentList(Resource):
    @api.doc('List of shipments registered on this node')
    @api.marshal_with(_shipment, as_list=True)
    @api.response(400, 'Malformed URL.')
    @api.response(500, 'Internal Server Error.')
    def get(self):
        """Returns shipments, known by this node, in a list"""
        try:
            return get_all_shipments()
        except Exception as e:
            api.abort(500)

    @api.doc('Register a new shipment')
    @api.expect(parser, _new_shipment, validate=True)
    @api.response(201, 'Shipment successfully created.')
    @api.response(400, 'Shipment input data is invalid.')
    @api.response(409, 'Shipment already exists.')
    @api.response(500, 'Internal Server Error.')
    @api.expect(parser)
    def post(self):
        """Register a new Shipment"""
        data = request.json
        try:
            return save_new_shipment(data=data)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)

@api.route('/rpc/import')
class ShipmentImport(Resource):
    @api.doc('Import a shipment from a peer')
    @api.expect(parser, _import_shipment, validate=True)
    @api.response(201, 'Shipment successfully created.')
    @api.response(400, 'Shipment input data is invalid.')
    @api.response(409, 'Shipment already exists.')
    @api.response(500, 'Internal Server Error.')
    @api.expect(parser)
    def post(self):
        """Import new Shipment from a peer"""
        data = request.json
        try:
            return receive_shipment_from_previous_peer(data=data)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)

@api.route('/<public_id>')
@api.param('public_id', 'The shipment identifier')
class Shipment(Resource):
    @api.doc('get a shipment')
    @api.marshal_with(_shipment)
    @api.response(404, 'Shipment not found.')
    @api.response(500, 'Internal Server Error.')
    def get(self, public_id):
        """Get details for a single shipment""" 
        try:
            return get_a_shipment(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)

@api.route('/<public_id>/positions')
@api.param('public_id', 'The shipment identifier')
class PositionsOfShipment(Resource):
    @api.doc('get positions of a shipment')
    @api.marshal_with(_position, as_list=True)
    @api.response(404, 'Shipment not found.')
    @api.response(500, 'Internal Server Error.')
    def get(self, public_id):
        """Get the positions of a shipment""" 
        try:
            return get_positions_of_a_shipment(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)

@api.route('/<public_id>/rpc/send')
@api.param('public_id', 'The shipment identifier')
class SendShipment(Resource):
    @api.doc('send shipment to the next company')
    @api.marshal_with(_position, as_list=True)
    @api.response(404, 'Shipment not found.')
    @api.response(500, 'Internal Server Error.')
    def post(self, public_id):
        """Send the shipment to the next peer""" 
        data = request.json
        try:
            return send_shipment_to_next_peer(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)
