# splunk-template-command

## Introduction

This add-on is intended to be a Search Command Template with the intent of simplifying setup.xml, creating/managing the password store, and using custom config files.

This are created using parts of the JIRA Alert Add-on created by Splunk. You can clone this project.

## Using Template

1. Clone template from [Github](git@github.com:httpstergeek/splunk-template-command.git)
2. Rename `splunk-template-command` directory to your `<newAppName>`.
3. Update app.conf to setting to reflect your app.
    * if you plan on using the credential store for password update the credentials stanza.
4. For custom config files rename `customcommand.conf` and `customcommand.conf.spec` to a relevant name.
    * Update stanza and setting which you plan to using in your app.
5. Rename customcommand.py to reflect your <newAppName>.
6. Edit `commands.conf` replace stanza with the name of your custom command and replace `filename` settings with what ever you renameed customcommand.py to.
7. Update `restmap.conf`  the `[admin_external:command_install]` to `[admin_external:<newAppName>_install]`
8. Within `<newAppName>.py` from setup 5 search and replace `customCommand` with `<newAppName>`
    * Replace `customCommand`  with `<newAppName>` in logging.conf
9. Within setup.xml
    * edit the `endpoint` attribute to reflect the change made in step 7.
    * edit the `entity` attribute to reflect the stanza define in your custom conf file
    * edit all `field` attribute to reflect the settings defined in your custom conf file
10. Edit `install_endpoint.py` to reflect the stanza and setting define in `setup.xml` and your custom.conf file.

###Adding Python modules
Note: PIP is required and all modules should have no archType.

To add edit the setup.sh.


## License
The Splunk Add-on for Atlassian JIRA Alerts is licensed under the Apache License 2.0. Details can be found in the [LICENSE page](http://www.apache.org/licenses/LICENSE-2.0).