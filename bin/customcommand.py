#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2015 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.



from __future__ import absolute_import, division, print_function, unicode_literals

from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option
import sys
import json
from helpers import get_password, get_config, get_appName


@Configuration()
class customCommand(StreamingCommand):
    """ Counts the number of non-overlapping matches to a regular expression in a set of fields.
    ##Syntax
    .. code-block::
        customcommand fields="<field>,*"
    ##Description
    Example  of building a stream custom command.
    .. code-block::
        | inputlookup tweets | customcommand fields="<field>,*"
    """
    fields = Option(
        doc='''
        **Syntax:** **fields=***<fieldname>*
        **Description:** Comma seperated list of fields in results''',
        require=False)

    def stream(self, records):
        searchinfo = self.metadata.searchinfo

        password = get_password(searchinfo.splunkd_uri, searchinfo.session_key, get_appName())
        config = get_config('customcommand', local=True)

        # create outbound JSON message body
        fields = self.fields.split(',')

        for record in records:
            record['a_fields'] = '%s' % fields
            record['a_password'] = password
            record['a_combine'] = "%s%s" % (record['sourcetype'], record['source'])
            record['a_config'] = config
            record['a_command_metadata'] = '%s' % self.metadata

            yield record

dispatch(customCommand, sys.argv, sys.stdin, sys.stdout, __name__)


