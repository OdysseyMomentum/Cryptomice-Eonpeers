import datetime
import unittest

from app.main.services import db
from app.main.model.company import Company
from app.main.service.company_service import (get_locations_of_a_company, save_new_company, generate_creation_ok_message, get_a_company, get_node_owner, )
from app.test.base import BaseTestCase


class TestUserModel(BaseTestCase):

    DEBUG = False
    
    def test_create_company(self):
    	data = {
    		"name":"test_company",
    		"vat_number":"12345678",
    		"base_url":"http://localhost:5400",
    		"public_key":"123456787"
    	}

    	res = save_new_company(data)
    	self.assertTrue(res[1]==201)
    	self.assertTrue(res[0] and res[0]["public_id"])

    	company = get_a_company(res[0]["public_id"])

    	self.assertTrue(company.name == data["name"])

if __name__ == '__main__':
    unittest.main()
