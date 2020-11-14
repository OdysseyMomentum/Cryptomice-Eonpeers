from flask import request
from flask_restplus import Resource

from app.main.service.validation_service import (get_a_validation, sign_a_validation, create_new_validation, receive_a_validation)
from app.main.util.dto import ValidationDto
from app.main.util.decorator import admin_token_required, token_required
from app.main.util.eonerror import EonError

api = ValidationDto.api
_validation = ValidationDto.validation
_new_validation_request = ValidationDto.new_validation_request
_new_validation = ValidationDto.new_validation
_validation_to_sign = ValidationDto.validation_to_sign

parser = api.parser()
parser.add_argument('Authorization', location='headers', help="Auth token from login")

@api.route('/rpc/request-validation')
class ValidationRequest(Resource):
    @api.doc('Request a validation to be signed by the local company')
    @api.expect(parser, _new_validation_request, validate=True)
    @api.response(201, 'Validation successfully created and pending.')
    @api.response(400, 'Validation input data is invalid.')
    @api.response(500, 'Internal Server Error.')
    def post(self):
        """Request a new Validation from another note"""
        data = request.json
        try:
            return create_new_validation(data=data)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)

@api.route('/')
class ValidationList(Resource):
    @api.doc('post a validation')
    @api.expect(parser, _new_validation, validate=True)
    @api.response(404, 'Validation not found.')
    @api.response(500, 'Internal Server Error.')
    def post(self):
        """Receive a signed validation""" 
        data = request.json
        try:
            return receive_a_validation(data=data)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)


@api.route('/<public_id>')
@api.param('public_id', 'The validation identifier')
class Validation(Resource):
    @api.doc('get a validation')
    @api.marshal_with(_validation)
    @api.response(404, 'Validation not found.')
    @api.response(500, 'Internal Server Error.')
    def get(self, public_id):
        """Get details for a single validation""" 
        try:
            return get_a_validation(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)

@api.route('/<public_id>/rpc/sign')
@api.param('public_id', 'The validation identifier')
class ValidationConfirm(Resource):
    @api.doc('Sign an existing validation')
    @api.expect(parser, _validation_to_sign, validate=True)
    @api.response(200, 'Validation successfully updated.')
    @api.response(404, 'Validation not found.')
    @api.response(409, 'Conflicts with the request, detailed message included')
    @api.response(500, 'Internal Server Error.')
    def put(self, public_id):
        """Sign an existing validation - Node Admin only"""
        try:
            data = request.json
            return sign_a_validation(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)