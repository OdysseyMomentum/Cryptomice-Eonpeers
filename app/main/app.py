from flask import Blueprint, Flask
from flask_restplus import Api

from app.main.config import config_by_name
from app.main.controller.auth_controller import api as auth_ns
from app.main.controller.user_controller import api as user_ns
from app.main.controller.company_controller import api as company_ns
from app.main.controller.location_controller import api as location_ns
from app.main.controller.validation_controller import api as validation_ns
from app.main.controller.shipment_controller import api as shipment_ns
from app.main.controller.position_controller import api as position_ns
from app.main.services import db, flask_bcrypt
from app.main.celery import init_celery


def create_app(**kwargs):
    """ create the flask app, then initalise the services: db, bycrypt, celery; finally preapre the api blueprint"""
    config_name=kwargs.get("config_name")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    flask_bcrypt.init_app(app)
    if(kwargs.get("celery")):
      init_celery(kwargs.get("celery"), app)

    blueprint = Blueprint('api', __name__)
    api = Api(blueprint,
              title='EONPEERS',
              version='1.0',
              description='Eonpeers restplus web service with JWT')
    api.add_namespace(user_ns, path='/user')
    api.add_namespace(auth_ns)
    api.add_namespace(company_ns, path='/company')
    api.add_namespace(location_ns, path='/location')
    api.add_namespace(validation_ns, path='/validation')
    api.add_namespace(shipment_ns, path='/shipment')
    api.add_namespace(position_ns, path='/position')
    app.register_blueprint(blueprint)

    app.app_context().push()

    return app
