from flask import request
from flask_restplus import Resource

from app.main.service.user_service import (get_a_user, get_all_users, save_new_user)
from app.main.util.dto import UserDto
from app.main.util.decorator import admin_token_required, token_required

api = UserDto.api
_user = UserDto.user
_new_user = UserDto.new_user

parser = api.parser()
parser.add_argument('Authorization', location='headers', help="Auth token from login")

@api.route('/')
class UserList(Resource):
    @api.doc('list of registered users')
    @api.marshal_list_with(_user, envelope='data')
    @api.expect(parser)
    @admin_token_required
    def get(self):
        """List all registered users"""
        return get_all_users()

    @api.response(201, 'User successfully created.')
    @api.doc('create a new user')
    @api.expect(_new_user, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)


@api.route('/<public_id>')
@api.param('public_id', 'The User identifier')
@api.response(404, 'User not found.')
class User(Resource):
    @api.doc('get a user')
    @api.marshal_with(_user)
    def get(self, public_id):
        """get a user given its identifier"""
        user = get_a_user(public_id)
        if not user:
            api.abort(404)
        else:
            return user
