
__author__ = ''

import splunk
import splunk.admin as admin
from helper import *

PASSWORD_PLACEHOLDER = '*******'

class JiraAlertsInstallHandler(admin.MConfigHandler):
    def __init__(self, *args):
        admin.MConfigHandler.__init__(self, *args)
        self.shouldAutoList = False

    def setup(self):
        self.supportedArgs.addOptArg('*')

    def handleList(self, confInfo):
        settings = get_settings(splunk.getLocalServerInfo(), self.getSessionKey())
        item = confInfo['command']
        item['url'] = settings.get('url', 'http://your.server/')
        item['username'] = settings.get('username')
        item['password'] = PASSWORD_PLACEHOLDER

    def handleEdit(self, confInfo):
        if self.callerArgs.id == 'command':
            settings = get_jira_settings(splunk.getLocalServerInfo(), self.getSessionKey())
            if 'url' in self.callerArgs:
                settings['url'] = self.callerArgs['url'][0]
            if 'username' in self.callerArgs:
                settings['username'] = self.callerArgs['username'][0]
            if 'password' in self.callerArgs:
                password = self.callerArgs['password'][0]
                if password and password != PASSWORD_PLACEHOLDER:
                    settings['customcommand_password'] = password
            update_jira_settings(jira_settings, splunk.getLocalServerInfo(), self.getSessionKey())

admin.init(JiraAlertsInstallHandler, admin.CONTEXT_APP_ONLY)