#!/usr/bin/env python
import os
import unittest
import app

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app.main.app import create_app
from app.main.model import blacklist  # noqa
from app.main.model import user  # noqa
from app.main.services import db
from app.main.celery import celery, setup_worker

app = create_app(config_name = os.getenv('EONCODES_ENV') or 'dev', celery = celery)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def run():
    """ Runs the flask server """
    app.run(host='0.0.0.0', port=5001)


@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def celery():
    """Runs celery worker."""
    from app.main.util import tasks  # noqa
    return setup_worker(celery, app)


@manager.option('-n', '--name', help='test class filename')
def singletest(name):
    """Runs the specified test class."""
    tests = unittest.TestLoader().discover('app/test', pattern=name)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
