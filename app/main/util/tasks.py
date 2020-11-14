from flask import current_app
from app.main.celery import celery
from celery.utils.log import get_task_logger
from app.main.services import db
import requests, json
from app.main.model.company import Company
from app.main.model.location import Location
from app.main.model.validation import Validation
from app.main.util.keymanagementutils import KeyManagementClient

logger = get_task_logger(__name__)

def make_gossip_call(*args):
    """ 
    Exectue the desired HTTP method on the url 

    the headers are optional, the response is returned
    although it may be ignored if when calling the task
    the ignore_result is set

    Parameters
    ----------
    args[0]: str
        the method, can be 'get','post','put'

    args[1]: str
        base_url, must have the complete url from http... 

    args[2]: dict
        the JSON to be sent as payload for put and post requests

    args[3]: dict
        the headers to be added 

    Response
    --------

    Raises
    ------

    """
    method = args[0]
    url = args[1]
    payload = {} if (len(args)<=2) else args[2]
    headers = {} if (len(args)<=3) else args[3]

    try:
        if(method=='get'):
            return requests.get(url,headers=headers)
        elif(method=='post'):
            r = requests.post(url,data=payload,headers=headers)
            print(r.content)
            return r
        elif(method=='put'):
            return requests.put(url,data=payload,headers=headers)
        else:
            return
    except Exception as general_exception:
        print(str(general_exception))
        return {'error': "An Exception occured: " + str(general_exception)}

@celery.task()
def validate_new_company(base_url, public_id):
    """ 
    GET the owner data and compare it against the local copy, if all checks out ACK, else destroy local company

    the method calls the remote system for its owner data, then compares it against the
    local public_id of the company that has been created with the initial POST.
    Empty data is filled, but if an incongruence is found the company is destroyed

    Parameters
    ----------
    base_url: str
        the endpoint to query must have the complete url from http... to /owner
    public_id: str
        the local id of the company 

    Response
    --------

    Raises
    ------

    """
    res = make_gossip_call("get", base_url)
    remote_company = res.json()

    local_company = Company.query.filter_by(public_id=public_id).first()

    fields = ['name','vat_number','public_key']
    error_flag = False
    for field in fields:
        if(getattr(local_company, field) == None):
            setattr(local_company, field, remote_company[field])
        if(getattr(local_company, field) != remote_company[field]):
            db.session.delete(local_company)
            db.session.commit()
            error_flag = True
            break
    if not error_flag:
        db.session.add(local_company)
        db.session.commit()
    return

@celery.task()
def validate_remote_location(location_id, validation_id):
    """ 
    POST the validation data to the requeting company

    After the validation is signed, the requeting company is notified
    that the signature has been done. The data payload passed back to
    the requesting company contains all the details so that they can 
    save the validaiton in their db and link it back to us

    Parameters
    ----------
    location_id: str
        the local id of the location 
    validation_id: str
        the local id of the validaiton (signed)

    Response
    --------

    Raises
    ------

    """

    location = Location.query.filter_by(public_id=location_id).first()
    validation = Validation.query.filter_by(public_id=validation_id).first()
    requesting_company = Company.query.filter_by(public_id=location.company_id).first()
    kmc = KeyManagementClient()
    payload = {
        "location_key": location.location_key,
        "signed_location_key": validation.signed_location_key,
        "signer_public_key": kmc.get_serialized_pub_key().decode("utf-8"),
        "signer_validation_id": validation_id
    }
    url = requesting_company.base_url if requesting_company.base_url[-1]=='/' else requesting_company.base_url+'/'
    url+='validation/'
    payload = json.dumps(payload) 
    headers = {"Content-Type":"application/json", "accept":"application/json"}
    make_gossip_call('post', url, payload, headers) 
    #TODO: use headers and registr user when companies registers
    return

@celery.task()
def send_shipment(payload, next_company_id):
    """
    POST this shipment to the destination node


    """  
    try:        
        target_company = Company.query.filter_by(public_id=next_company_id).first()
        url = target_company.base_url if target_company.base_url[-1]=='/' else target_company.base_url+'/'
        url+='shipment/rpc/import'
        payload = json.dumps(payload) 
        headers = {"Content-Type":"application/json", "accept":"application/json"}
        make_gossip_call('post', url, payload, headers)     
        #TODO: use authentication to post
    except Exception as e:
        print(e)
    return

