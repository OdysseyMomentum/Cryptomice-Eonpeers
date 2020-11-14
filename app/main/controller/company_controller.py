from flask import request
from flask_restplus import Resource

from app.main.service.company_service import (get_a_company, get_all_companies, save_new_company, get_node_owner, get_locations_of_a_company)
from app.main.util.dto import CompanyDto, LocationDto
from app.main.util.decorator import admin_token_required, token_required
from app.main.util.eonerror import EonError

api = CompanyDto.api
_company = CompanyDto.company
_new_company = CompanyDto.new_company
_node_owner_company = CompanyDto.node_owner_company
_location = LocationDto.location

parser = api.parser()
parser.add_argument('Authorization', location='headers', help="Auth token from login")

@api.route('/')
class CompanyList(Resource):
    @api.doc('List of companies registere on this node')
    @api.marshal_with(_company, as_list=True)
    @api.response(400, 'Malformed URL.')
    @api.response(500, 'Internal Server Error.')
    def get(self):
        """Returns companies, known by this node, in a list"""
        try:
            return get_all_companies()
        except Exception as e:
                api.abort(500)

    @api.doc('Register a new company')
    @api.expect(parser, _new_company, validate=True)
    @api.response(201, 'Company successfully created.')
    @api.response(400, 'Company input data is invalid.')
    @api.response(409, 'Company already exists.')
    @api.response(500, 'Internal Server Error.')
    @api.expect(parser)
    def post(self):
        """Register a new Company"""
        data = request.json
        try:
            return save_new_company(data=data)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)


@api.route('/<public_id>')
@api.param('public_id', 'The company identifier')
class Company(Resource):
    @api.doc('get a company')
    @api.marshal_with(_company)
    @api.response(404, 'Company not found.')
    @api.response(500, 'Internal Server Error.')
    def get(self, public_id):
        """Get details for a single company""" 
        try:
            return get_a_company(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)

@api.route('/<public_id>/locations')
@api.param('public_id', 'The company identifier')
class LocationsOfCompany(Resource):
    @api.doc('get locations of a company')
    @api.marshal_with(_location, as_list=True)
    @api.response(404, 'Company not found.')
    @api.response(500, 'Internal Server Error.')
    def get(self, public_id):
        """Get the locations of a company""" 
        try:
            return get_locations_of_a_company(public_id)
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)


@api.route('/node-owner')
class NodeOwnerCompany(Resource):
    @api.doc('get the company owning this node')
    @api.marshal_with(_node_owner_company)
    @api.response(500, 'Internal Server Error.')
    def get(self):
        """Get details of the company running this node""" 
        try:
            return get_node_owner()
        except EonError as e:
            if(e.code and e.message):
                api.abort(e.code, e.message)
            else:
                api.abort(500)

