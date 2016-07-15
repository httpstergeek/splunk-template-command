__author__ = ''
import sys
import requests
import json
import os
import platform
try:
    from splunk.clilib import cli_common as cli
except:
    pass

def splunkd_auth_header(session_key):
    """
    Building dict for request headers
    :param session_key:
    :return:
    """
    return {'Authorization': 'Splunk ' + session_key}

def update_settings(settings, server_uri, session_key, conf, password_store):
    """
    Updates config file and password store
    :param settings:
    :param server_uri:
    :param session_key:
    :param conf:
    :param password_store:
    :return:
    """
    app = get_appName()
    url = "%s%s%s%s%s%s" % (server_uri, '/servicesNS/nobody/', app,'/storage/passwords/%3A', password_store,'%3A?output_mode=json')
    requests.post(
        url=url,
        data={
            'password': settings.pop(password_store, None)
        },
        headers=splunkd_auth_header(session_key),
        verify=False)
    update_config(conf, settings)


def get_settings(server_uri, session_key, conf, password_store):
    """
    Retrieves merged custom config file and password
    :param server_uri:
    :param session_key:
    :param conf:
    :param password_store:
    :return:
    """
    results = get_config(conf, local=True)
    results[password_store] = get_password(server_uri, session_key, password_store)
    return results

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


def get_password(server_uri, session_key, password_store):
    """
    Retrives password from store in plain text
    :param server_uri:
    :param session_key:
    :param password_store:
    :return:
    """
    app = get_appName()
    password_url = "%s%s%s%s%s%s" % (server_uri, '/servicesNS/nobody/', app,
                                     '/storage/passwords/%3A', password_store, '%3A?output_mode=json')
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


def get_config(conf, local=False):
    """
    Creates a dictionary fo dicts for uses in Sorkin .conf file.
    This function creates parity for use with writeConfFile in splunk.clilib
    :pram local: local config only
    :param conf: Splunk conf file file name
    :return: dictionary of dicts
    """
    appdir = os.path.dirname(os.path.dirname(__file__))
    conf = "%s.conf" % conf
    defaultconfpath = os.path.join(appdir, "default", conf)
    stanzaDict = cli.readConfFile(defaultconfpath) if os.path.exists(defaultconfpath) else {}
    localconfpath = os.path.join(appdir, "local", conf)
    if not local:
        if os.path.exists(localconfpath):
            localconf = cli.readConfFile(localconfpath)
            for setting, stanza in localconf.items():
                if setting in stanzaDict:
                    stanzaDict[setting].update(stanza)
                else:
                    stanzaDict[setting] = stanza
    else:
        stanzaDict = cli.readConfFile(localconfpath) if os.path.exists(localconfpath) else {}
    return stanzaDict

def get_appName():
    """
    Returns current app context
    :return:
    """
    appdir = os.path.dirname(os.path.dirname(__file__))
    splitby = '/' if not (platform.system() == 'Windows') else '\\'
    app = appdir.split(splitby)[-1]
    return app
