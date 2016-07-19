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

# TODO rewrite as class.  Duplicate calls for get_appName and get_passwordstore_name

def splunkd_auth_header(session_key):
    """
    Building dict for request headers
    :param session_key:
    :return:
    """
    return {'Authorization': 'Splunk ' + session_key}

def update_settings(settings, server_uri, session_key, conf):
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
    password_store = get_passwordstore_name(server_uri, session_key, app)
    url = "%s%s%s%s%s%s" % (server_uri, '/servicesNS/nobody/', app,'/storage/passwords/%3A', password_store,'%3A?output_mode=json')
    requests.post(
        url=url,
        data={
            'password': settings.pop(password_store)
        },
        headers=splunkd_auth_header(session_key),
        verify=False)
    update_config(conf, settings)


def get_settings(server_uri, session_key, conf):
    """
    Retrieves merged custom config file and password
    :param server_uri:
    :param session_key:
    :param conf:
    :param password_store:
    :return:
    """
    results = get_config(conf, local=True)
    app = get_appName()
    password_store = get_passwordstore_name(server_uri, session_key, app)
    results[password_store] = get_password(server_uri, session_key, app)
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


def get_password(server_uri, session_key, app):
    """
    Retrives password from store in plain text
    :param server_uri:
    :param session_key:
    :return:
    """
    password_store = get_passwordstore_name(server_uri, session_key, app)

    try:
        password_url = "%s%s%s%s%s%s" % (server_uri, '/servicesNS/nobody/', app,
                                         '/storage/passwords/%3A', password_store, '%3A?output_mode=json')

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

def get_passwordstore_name(server_uri, session_key, app):
    app_properties_url = "%s%s%s%s" % (server_uri, '/servicesNS/nobody/', app, '/properties/app?output_mode=json')
    try:
        result = requests.get(url=app_properties_url, headers=splunkd_auth_header(session_key), verify=False)
        if result.status_code != 200:
            print >> sys.stderr, "ERROR Error: %s" % str(result.json())
    except Exception, e:
        print >> sys.stderr, "ERROR Error sending message: %s" % e
        return False

    splunk_response = json.loads(result.text)
    for entry in splunk_response['entry']:
        if "credential" in entry['name']:
            password_store = entry['name'].replace('credential::','').strip(':')
            break
        else:
            password_store = None
    return password_store


class AppConf:
    def __init__(self, server_uri, session_key):
        self.server_uri = server_uri
        self.session_key = session_key
        self.appdir = os.path.dirname(os.path.dirname(__file__))
        self.app = self._get_appname()
        self.password_store = self._password_store()


    def get_config(self, conf, local=False):
        """
        Retrieves local or merged dictionary of dicts local app context.
        This function creates parity for use with writeConfFile in splunk.clilib
        :pram local: local config only
        :param conf: Splunk conf file file name
        :return: dictionary of dicts
        """
        conf = "%s.conf" % conf
        defaultconfpath = os.path.join(self.appdir, "default", conf)
        stanzaDict = cli.readConfFile(defaultconfpath) if os.path.exists(defaultconfpath) else {}
        localconfpath = os.path.join(self.appdir, "local", conf)
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

    def get_password(self):
        """
        Retrives password from store in plain text
        :return:
        """
        password_url = "%s%s%s%s%s%s" % (self.server_uri, '/servicesNS/nobody/', self.app,
                                         '/storage/passwords/%3A', self.password_store, '%3A?output_mode=json')
        splunk_response = self._get_endpoint(password_url)
        password = splunk_response.get("entry")[0].get("content").get("clear_password")
        return password

    def get_settings(self, conf):
        """
        Retrieves merged custom config file and password
        :param conf:
        :return:
        """
        results = self.get_config(conf, local=True)
        results[self.password_store] = self.get_password()
        return results

    def update_config(self, conf, stanzaDict):
        """
        Writes dictionary of dicts to local app context
        :param conf: Splunk conf file name
        :param stanzaDict: dictionary of dicts
        :return: True
        """
        conf = "%s.conf" % conf
        localconfpath = os.path.join(self.appdir, "local", conf)
        cli.writeConfFile(localconfpath, stanzaDict)
        return True

    def update_settings(self, conf, stanzaDict):
        """
        Updates config file and password store.
        :param conf: Splunk conf file name
        :param stanzaDict: dictionary of dicts
        :return:
        """
        url = "%s%s%s%s%s%s" % (self.server_uri, '/servicesNS/nobody/', self.app,
                                '/storage/passwords/%3A', self.password_store, '%3A?output_mode=json')
        try:
            result = requests.post(url=url,
                                   data={'password': stanzaDict.pop(self.password_store)},
                                   headers=self._splunkd_auth_header(),
                                   verify=False)
            if result.status_code != 200:
                print >> sys.stderr, "ERROR Error: %s" % result.json()
        except Exception, e:
            print >> sys.stderr, "ERROR Error sending message: %s" % e
            return False
        return self.update_config(conf, stanzaDict)

    def _get_appname(self):
        """
        Returns current app context
        :return:
        """
        splitby = '/' if not (platform.system() == 'Windows') else '\\'
        app = self.appdir.split(splitby)[-1]
        return app

    def _password_store(self):
        """
        returns password store definition from app.conf
        :return:
        """
        app_properties_url = "%s%s%s%s" % (self.server_uri, '/servicesNS/nobody/',
                                           self.app, '/properties/app?output_mode=json')
        splunk_response = self._get_endpoint(app_properties_url)
        password_store = None
        for entry in splunk_response['entry']:
            if "credential" in entry['name']:
                password_store = entry['name'].replace('credential::', '').strip(':')
                break
        return password_store

    def _splunkd_auth_header(self):
        """
        Building dict for request headers
        :return:
        """
        return {'Authorization': 'Splunk ' + self.session_key}

    def _get_endpoint(self, url):
        try:
            # attempting to retrieve cleartext password, disabling SSL verification for practical reasons
            result = requests.get(url=url, headers=self._splunkd_auth_header(), verify=False)
            if result.status_code != 200:
                print >> sys.stderr, "ERROR Error: %s" % str(result.json())
        except Exception, e:
            print >> sys.stderr, "ERROR Error sending message: %s" % e
            return False
        return json.loads(result.text)
