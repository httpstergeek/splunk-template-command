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
from helper import get_password, get_config


@Configuration()
class CustomCommand(StreamingCommand):
    """ Counts the number of non-overlapping matches to a regular expression in a set of fields.
    ##Syntax
    .. code-block::
        countmatches fieldname=<field> pattern=<regular_expression> <field-list>
    ##Description
    A count of the number of non-overlapping matches to the regular expression specified by `pattern` is computed for
    each record processed. The result is stored in the field specified by `fieldname`. If `fieldname` exists, its value
    is replaced. If `fieldname` does not exist, it is created. Event records are otherwise passed through to the next
    pipeline processor unmodified.
    ##Example
    Count the number of words in the `text` of each tweet in tweets.csv and store the result in `word_count`.
    .. code-block::
        | inputlookup tweets | countmatches fieldname=word_count pattern="\\w+" text
    """
    fields = Option(
        doc='''
        **Syntax:** **fields=***<fieldname>*
        **Description:** Comma seperated list of fields in results''',
        require=False)

    def stream(self, records):
        searchinfo = self.metadata.searchinfo
        password = get_password(searchinfo.splunkd_uri, searchinfo.session_key)
        config = get_config(searchinfo.splunkd_uri, searchinfo.session_key)

        # create outbound JSON message body
        fields = self.fields.split(',')

        for record in records:
            record['fields'] = '%s' % fields
            record['password'] = password
            record['config'] = config
            record['command_metadata'] = '%s' % self.metadata
            yield record

dispatch(CustomCommand, sys.argv, sys.stdin, sys.stdout, __name__)


