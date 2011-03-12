# Copyright (c) 2006-2010 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2010, Eucalyptus Systems, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

try:
    import json
except ImportError:
    import simplejson as json
import os
import boto

class JSONFile(object):

    def __init__(self, provider, service_name, request_name=None):
        self.provider = provider
        self.service_name = service_name
        self.request_name = request_name
        self.json_dir = self._get_json_dir()
        self.data = self._load_json()
        
    def _get_json_dir(self, section_name='roboto', option_name='json_dir'):
        if boto.config.has_section(section_name):
            if boto.config.has_option(section_name, option_name):
                json_dir = boto.config.get_value(section_name, option_name)
                json_dir = os.path.expanduser(json_dir)
                json_dir = os.path.expandvars(json_dir)
                return json_dir
        else:
            raise ValueError('No value for json_dir found in boto config')

    def _load_json(self):
        json_path = os.path.join(self.json_dir, self.provider)
        json_path = os.path.join(json_path, self.service_name)
        if self.request_name:
            json_path = os.path.join(json_path, self.request_name)
        json_path += '.json'
        if os.path.isfile(json_path):
            fp = open(json_path)
            s = fp.read()
            fp.close()
            return json.loads(s)
        else:
            print 'Unable to find JSON file: %s' % json_path
            
