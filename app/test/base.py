from flask_testing import TestCase

import requests
from app.main.services import db
from manage import app


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object('app.main.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def requestNewTestBlock(self):
        url = "http://"+app.config['RPC_HOST']+":5000/block"
        headers = {'Api-Key': app.config['TEST_EXPLORER_PASSWORD']}
        req = requests.put(url, data = {'blocks':1}, headers=headers)
