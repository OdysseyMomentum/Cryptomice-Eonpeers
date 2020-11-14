import os
from celery import Celery
from app.main.config import config_by_name

def init_celery(celery, app):
    """ After celery is made, create_app adds its context """

    ## TODO: when init celery it could be a good idea to update the config with the app config
    # understand if this is necessary/good or not.
    # the point is, in app.config you have keys like DEFAULT_CEELRY_BROKER, which are ok for creation but 
    # should be updated to the new syntax for conf.update: DEFAULT_CEELRY_BROKER -> celery_broker
    #celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

def make_celery(app_name=__name__):
    """ create the celery app loading parameters from the config file and the env variable """

    config = config_by_name[os.getenv('EONFLASK_ENV') or 'dev']
    broker = config.CELERY_BROKER_URL
    backend = config.CELERY_RESULT_BACKEND if config.CELERY_RESULT_BACKEND else broker
    celery = Celery(
        app_name,
        broker=broker,
        backend=backend
    )
    celery.conf.result_expires = 600
    return celery


celery = make_celery()

def setup_worker(celery, app):
    cel = make_celery()
    worker = cel.Worker(
        concurrency=1,
        loglevel='info',
        autoreload=True)
    worker.start()
    return worker.exitcode