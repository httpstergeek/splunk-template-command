import splunk
import requests
import json
import sys
import unittest
from xml.dom import minidom
from jira_helpers import *

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

# TODO:  add unit tests.

