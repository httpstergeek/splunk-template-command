import splunk
import requests
import json
import sys
import unittest
from xml.dom import minidom
from helpers import *

'''
    This unit test checks:
        * The validity of a sample JSON payload intended to
          be sent to JIRA.

        * The ability of the JIRA Add-on to pull a JIRA username
          & password from the indicated Splunk instance.

    Asserts that necessary default values have been changed
    and for the existence of required keys.
    
    Set values for SPLUNK_URL, SPLUNK_USERNAME & SPLUNK_PASSWORD
    prior to executing unit tests.
'''
class TestJiraClass(unittest.TestCase):
    SPLUNK_URL = ""
    SPLUNK_USERNAME = ""
    SPLUNK_PASSWORD = ""

    @classmethod
    def setUpClass(cls):
        if cls.SPLUNK_URL is "" or cls.SPLUNK_USERNAME is "" or cls.SPLUNK_PASSWORD is "":
            print >> sys.stdout, "Please set Splunk configuration bits before executing test script."
            sys.exit(1)

        try:
            # obtaining splunk session key
            result = requests.post(url=cls.SPLUNK_URL + "/services/auth/login", data={'username':cls.SPLUNK_USERNAME, 'password':cls.SPLUNK_PASSWORD}, headers={}, verify=False)
            cls.session_key = minidom.parseString(result.text).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
        except Exception, e:
            print >> sys.stderr, "ERROR Unable to parse JSON file.  Error: %s" % e

class TestJiraPayload(TestJiraClass):
    @classmethod
    def setUpClass(cls):
        super(TestJiraPayload, cls).setUpClass()

    # verifies that app property returns current app context
    def test_app(self):
        app = AppConf(self.SPLUNK_URL, self.session_key).app
        self.assertEqual(app, "splunk-template-command")

    # verifies that a password store name match whats defined in app.conf
    def test_password_store(self):
        password_store = AppConf(self.SPLUNK_URL, self.session_key).password_store
        self.assertEqual(password_store, "customcommand_password")

    # verifies that a password has been set in the Splunk instance
    def test_password(self):
        password = AppConf(self.SPLUNK_URL, self.session_key).get_password()
        self.assertNotEqual(password, None)


if __name__ == '__main__':
    unittest.main()