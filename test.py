import unittest
from mailjet_rest import Client, __version__
import os
import random
import string


class TestSuite(unittest.TestCase):

    def setUp(self):
        self.auth = (
            os.environ['MJ_APIKEY_PUBLIC'],
            os.environ['MJ_APIKEY_PRIVATE']
        )
        self.client = Client(auth=self.auth)

    def test_get_no_param(self):
        result = self.client.contact.get().json()
        self.failUnless(('Data' in result and 'Count' in result))

    def test_get_valid_params(self):
        result = self.client.contact.get(filters={'limit': 2}).json()
        self.failUnless('Count' >= 0 or result['Count'] <= 2)

    def test_get_invalid_parameters(self):
        # invalid parameters are ignored
        result = self.client.contact.get(filters={'invalid': 'false'}).json()
        self.failUnless('Count' in result)

    def test_get_with_data(self):
        # it shouldn't use data
        result = self.client.contact.get(data={'Email': 'api@mailjet.com'})
        self.failUnless(result.status_code == 200)

    def test_get_with_action(self):
        result_contact = self.client.contactslist.get(filters={'limit': 1}).json()

        if result_contact['Count'] is not 0:
            contact_id = result_contact['Data'][0]['ID']
        else:
            contact_random_email = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + '@mailjet.com'
            post_contact = self.client.contact.create(data={'Email': contact_random_email})
            self.failUnless(post_contact.status_code == 201)
            contact_id = post_contact.json()['Data'][0]['ID']

        result = self.client.contact_getcontactslists.get(contact_id).json()
        self.failUnless(result['Count'] > 1)

    def test_get_with_id_filter(self):
        result_contact = self.client.contact.get(filters={'limit': 1}).json()
        result_contact_with_id = self.client.contact.get(filter={'Email': result_contact['Data'][0]['Email']}).json()
        self.failUnless(result_contact_with_id['Data'][0]['Email'] == result_contact['Data'][0]['Email'])

    def test_post_with_no_param(self):
        result = self.client.sender.create(data={}).json()
        self.failUnless('StatusCode' in result and result['StatusCode'] is not 400)

    def test_client_custom_version(self):
        self.client = Client(
            auth=self.auth,
            version='v3.1'
        )
        self.assertEqual(self.client.config.version, 'v3.1')
        self.assertEqual(
            self.client.config['send'][0],
            'https://api.mailjet.com/v3.1/send'
        )

    def test_user_agent(self):
        self.client = Client(
            auth=self.auth,
            version='v3.1'
        )
        self.assertEqual(self.client.config.user_agent, 'mailjet-apiv3-python/'+__version__)


if __name__ == '__main__':
    unittest.main()
