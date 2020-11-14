from functools import wraps

from flask import request

from app.main.service.auth_helper import Auth


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data, status = Auth.get_logged_in_user(request)
        token = data.get('data')
        if not token:
            return data, status
        return f(*args, **kwargs)
    return decorated


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data, status = Auth.get_logged_in_user(request)
        token = data.get('data')
        if not token:
            return data, status
        admin = token.get('admin')
        if not admin:
            response_object = {
                'status': 'fail',
                'message': 'admin token required'
            }
            return response_object, 401
        return f(*args, **kwargs)
    return decorated

# THIS IS DONE WITH THE DTO OBJECTS! --->
# check if the json has the field(s) described in the arguments
# must be decorate the function which handles the JSON
# (which has request.get_json())
# e.g. check the post json has the field "id":
# @app.route("/someroute", methods=["POST"])
# @validate_json("id")
# def someFunction():
#     json_data= request.get_json()
#     ...
def validate_json(*expected_args):
    def decorator_validate_json(f):
        @wraps(f)
        def wrapper_validate_json(*args, **kwargs):
            json_object = request.get_json()
            for expected_arg in expected_args:
                if expected_arg not in json_object:
                    response_object = {
                        'status': 'fail',
                        'message': 'requried field missing',
                        'errors': [
                            {
                                'status': '400',
                                "title":  "Attribute Missing",
                                "detail": expected_arg+" missing from JSON"
                            }
                        ]
                    }
                    return response_object, 400
            return f(*args, **kwargs)
        return wrapper_validate_json
    return decorator_validate_json




def log_error(logger):
    """ Decorator that logs the exception and re-rasies it """
    def decorated(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.exception(e)
                raise
        return wrapped
    return decorated
