from flask import request
from flask_restplus import Resource

from app.main.service.auth_helper import Auth
from app.main.util.decorator import validate_json
from app.main.util.dto import AuthDto
from app.main.util.decorator import admin_token_required, token_required

api = AuthDto.api
user_auth = AuthDto.user_auth

parser = api.parser()
parser.add_argument('Authorization', location='headers', help="Auth token from login")


@api.route('/login')
class UserLogin(Resource):
    """
        User Login Resource
    """
    @api.doc('user login')
    @api.expect(user_auth, validate=True)
    @validate_json("email", "password")
    def post(self):
        # get the post data
        post_data = request.json
        return Auth.login_user(data=post_data)


@api.route('/logout')
class LogoutAPI(Resource):
    """
    Logout Resource
    """
    @api.doc('logout a user')
    @api.expect(parser)
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        return Auth.logout_user(data=auth_header)
