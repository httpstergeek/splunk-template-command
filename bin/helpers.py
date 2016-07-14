__author__ = ''
import sys
import requests
import json

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

    def get_password(server_uri, session_key, **kwargs):
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

    def get_jira_action_config(server_uri, session_key):
        url = server_uri + '/servicesNS/nobody/jira-send-command/configs/inputs/jirasend?output_mode=json'
        result = requests.get(url=url, headers=splunkd_auth_header(session_key), verify=False)
        return json.loads(result.text)['entry'][0]['content']