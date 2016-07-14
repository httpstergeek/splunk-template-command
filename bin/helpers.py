__author__ = ''
import sys
import requests
import json
import os
try:
    from splunk.clilib import cli_common as cli
except:
    pass

def splunkd_auth_header(session_key):
    return {'Authorization': 'Splunk ' + session_key}

def update_settings(settings, server_uri, session_key):
    r = requests.post(
        url=server_uri+'/servicesNS/nobody/jira-send-command/configs/inputs/jirasend?output_mode=json',
        data={
            'url': settings.get('url'),
            'username': settings.get('username')
        },
        headers=splunkd_auth_header(session_key),
        verify=False).json()
    requests.post(
        url=server_uri + '/servicesNS/nobody/jira-send-command/storage/passwords/%3Ajirasend_password%3A?output_mode=json',
        data={
            'password': settings.get('customcommand_password')
        },
        headers=splunkd_auth_header(session_key),
        verify=False)

def update_config(conf, stanzaDict):
    """
    Writes dictionary of dicts to local directory of app
    :param conf: Splunk conf file name
    :param stanzaDict: dictionary fo dicts for uses in Sorkin .conf file.
    :return: True
    """
    appdir = os.path.dirname(os.path.dirname(__file__))
    conf = "%s.conf" % conf
    localconfpath = os.path.join(appdir, "local", conf)
    cli.writeConfFile(localconfpath, stanzaDict)
    return True



def get_password(server_uri, session_key, app, passwordkey):
    password_url = server_uri + '/servicesNS/nobody/jira-send-command/storage/passwords/%3Acustomcommand_password%3A?output_mode=json'

    try:
        # attempting to retrieve cleartext password, disabling SSL verification for practical reasons
        result = requests.get(url=password_url, headers=splunkd_auth_header(session_key), verify=False)
        if result.status_code != 200:
            print >> sys.stderr, "ERROR Error: %s" % str(result.json())
    except Exception, e:
        print >> sys.stderr, "ERROR Error sending message: %s" % e
        return False

    splunk_response = json.loads(result.text)
    password = splunk_response.get("entry")[0].get("content").get("clear_password")

    return password


def get_config(conf):
    """
    Creates a dictionary fo dicts for uses in Sorkin .conf file.
    This function creates parity for use with writeConfFile in splunk.clilib

    :param conf: Splunk conf file file name
    :return: dictionary of dicts
    """
    appdir = os.path.dirname(os.path.dirname(__file__))
    conf = "%s.conf" % conf
    defaultconfpath = os.path.join(appdir, "default", conf)
    stanzaDict = cli.readConfFile(defaultconfpath) if os.path.exists(defaultconfpath) else {}
    localconfpath = os.path.join(appdir, "local", conf)
    if os.path.exists(localconfpath):
        localconf = cli.readConfFile(localconfpath)
        for setting, stanza in localconf.items():
            if setting in stanzaDict:
                stanzaDict[setting].update(stanza)
            else:
                stanzaDict[setting] = stanza
    print stanzaDict
