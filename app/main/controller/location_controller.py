from flask import request
from flask_restplus import Resource

from app.main.service.location_service import (get_a_location, save_new_location)
from app.main.util.dto import LocationDto
from app.main.util.decorator import admin_token_required, token_required
from app.main.util.eonerror import EonError

api = LocationDto.api
_location = LocationDto.location
_new_location = LocationDto.new_location

parser = api.parser()
parser.add_argument('Authorization', location='headers', help="Auth token from login")

@api.route('/')
class LocationList(Resource):
    @api.doc('Register a new location')
    @api.expect(parser, _new_location, validate=True)
    @api.response(201, 'Location successfully created.')
    @api.response(400, 'Location input data is invalid.')
    @api.response(409, 'Location already exists.')
    @api.response(500, 'Internal Server Error.')
    def post(self):
        """Register a new Location"""
        data = request.json
        try:
            return save_new_location(data=data)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)


@api.route('/<public_id>')
@api.param('public_id', 'The location identifier')
class Location(Resource):
    @api.doc('get a location')
    @api.marshal_with(_location)
    @api.response(404, 'Location not found.')
    @api.response(500, 'Internal Server Error.')
    def get(self, public_id):
        """Get details for a single location""" 
        try:
            return get_a_location(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)