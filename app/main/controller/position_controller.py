from flask import request
from flask_restplus import Resource

from app.main.service.position_service import (get_a_position, get_all_positions, save_new_position, sign_a_position)
from app.main.util.dto import PositionDto
from app.main.util.decorator import admin_token_required, token_required
from app.main.util.eonerror import EonError

api = PositionDto.api
_position = PositionDto.position
_new_position = PositionDto.new_position
_position_to_sign = PositionDto.position_to_sign

parser = api.parser()
parser.add_argument('Authorization', location='headers', help="Auth token from login")

@api.route('/')
class PositionList(Resource):
    @api.doc('List of positions registered on this node')
    @api.marshal_with(_position, as_list=True)
    @api.response(400, 'Malformed URL.')
    @api.response(500, 'Internal Server Error.')
    def get(self):
        """Returns positions, known by this node, in a list"""
        try:
            return get_all_positions()
        except Exception as e:
            api.abort(500)

    @api.doc('Register a new position')
    @api.expect(parser, _new_position, validate=True)
    @api.response(201, 'Position successfully created.')
    @api.response(400, 'Position input data is invalid.')
    @api.response(409, 'Position already exists.')
    @api.response(500, 'Internal Server Error.')
    @api.expect(parser)
    def post(self):
        """Register a new Position"""
        data = request.json
        try:
            return save_new_position(data=data)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)


@api.route('/<public_id>')
@api.param('public_id', 'The position identifier')
class Position(Resource):
    @api.doc('get a position')
    @api.marshal_with(_position)
    @api.response(404, 'Position not found.')
    @api.response(500, 'Internal Server Error.')
    def get(self, public_id):
        """Get details for a single position""" 
        try:
            return get_a_position(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)


@api.route('/<public_id>/rpc/sign')
@api.param('public_id', 'The position identifier')
class PositionConfirm(Resource):
    @api.doc('Sign an existing position')
    @api.expect(parser, _position_to_sign, validate=True)
    @api.response(200, 'Position successfully updated.')
    @api.response(404, 'Position not found.')
    @api.response(409, 'Conflicts with the request, detailed message included')
    @api.response(500, 'Internal Server Error.')
    def put(self, public_id):
        """Sign an existing position - Node Admin only"""
        try:
            data = request.json
            return sign_a_position(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)
