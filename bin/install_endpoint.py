
__author__ = ''

import splunk
import splunk.admin as admin
from helpers import *

PASSWORD_PLACEHOLDER = '*******'

class InstallHandler(admin.MConfigHandler):
    def __init__(self, *args):
        admin.MConfigHandler.__init__(self, *args)
        self.shouldAutoList = False

    def setup(self):
        self.supportedArgs.addOptArg('*')

    def handleList(self, confInfo):
        app_conf = AppConf(splunk.getLocalServerInfo(), self.getSessionKey())
        config = app_conf.get_config('customcommand')
        settings = config['customcommand'] if 'customcommand' in config else {}
        item = confInfo['customcommand']
        item['url'] = settings['url'] if settings['url'] else 'http://your.server/'
        item['username'] = settings['username'] if settings['username'] else ''
        item['password'] = PASSWORD_PLACEHOLDER

    def handleEdit(self, confInfo):
        if self.callerArgs.id == 'customcommand':
            app_conf = AppConf(splunk.getLocalServerInfo(), self.getSessionKey())
            settings = app_conf.get_settings('customcommand')
            settings[self.callerArgs.id] = {}
            if 'url' in self.callerArgs:
                settings[self.callerArgs.id]['url'] = self.callerArgs['url'][0]
            if 'username' in self.callerArgs:
                settings[self.callerArgs.id]['username'] = self.callerArgs['username'][0]
            if 'password' in self.callerArgs:
                password = self.callerArgs['password'][0]
                if password and password != PASSWORD_PLACEHOLDER:
                    settings[app_conf.password_store] = password
            app_conf.update_settings('customcommand', settings)

admin.init(InstallHandler, admin.CONTEXT_APP_ONLY)