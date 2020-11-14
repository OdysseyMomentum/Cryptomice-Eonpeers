# EonPeers

## Description

This project is a prototype for a peer to peer system where companies validate, with an electronic signature, the shipment data they commit to. It will be maintained on GitLab: https://gitlab.com/Eonpass/eonpeers

The project is a Flask+RestPlus server which generates the swagger documentation to interact with it. Most endpoints follow the REST structure, custom actions are identified by the /rpc/ token in their url.


## Documentation

A protocol specifics document is in the works.

## Installation

> Parts of code are written for python3 (e.g. bytes to string conversions)

To use Eonpeers it is recommended to install virtualenvwrapper:

    pip3 install virtualenvwrapper

After cloning the repository:

    cd eoncodes
    mkvirtualenv eoncodes
    workon eoncodes
    pip3 install -r requirements.txt

Before launching you need to initialize the local db with SQLAlchemy (in fact its migration folder is excluded from this repository). These functions are wrapped by `manage.py`

    python manage.py db init

> if you are developing or testing, the default suggested db is SQLlite: to allow for ALTER TABLE you need to edit the `migration/env.py` by adding `render_as_batch=True,` at around line 85, in the `context.configure` instruction

    python manage.py db migrate --message 'initial database migration'
    python manage.py db upgrade

### Configuration options

The repository comes with a template config file (`config_template.py`) that you can clone and rename in `config.py`.
The basic configuration uses SQLlite as testing db and redis as broker/backend for celery. The other options are:

+ `KMI_TYPE`, the type of key management infrastructure, for testing and developing there's an implementation which creates a private key file in the project folder (`DEV`), the stanard one for production is under development `PYKMIP`.
+ `LOCAL_FLASK_PORT`, which port will be used for Flask in localhost
+ `EONPASS_USER`, `PWD` and `URL`, will be the details to connect Eonpeers to Eonpass for blockchain operations (like notarising the signatures). At the moment they are not used.
+ the final `key` is the one used to initialise `bcrypt` (standard for JWT tokens) and is passed via environment variable 


## Running

### Development / Test

Before running the server or the test, make sure your celery worker and broker are active:

    redis-server
    pythong manage.py celery

Running the tests:

    python manage.py test

Running a local development instance:

    python manage.py run



### Production

Eonpeers must be deployed under Gunicorn and Ngnix.
w.i.p.


## Directory structure

Eonpeers uses the following structure:

- `app/main` 
  - `controller`, the functions that describe the endpoints and create the swagger documentation
  - `model`, the SQLalchemy models
  - `service`, the business logics behind the endpoints described in the controllers
  - `util`, static utilities like KMI, decorators, dto, and (for now) celery tasks
- `/app/test` holds the tests
- `/migrations` the folder created by SQLalchemy on init


## Acknowledgments

This project is sponsored by [Eonpass][Eonpass] with the support of [Odyssey][Odyssey] as a research activity to see how distributed data about shipment can be created and validated.

[Eonpass]: https://eonpass.com
[Odyssey]: https://odyssey.org
