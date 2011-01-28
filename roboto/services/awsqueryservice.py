# Copyright (c) 2010 Mitch Garnaat http://garnaat.org/
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

try:
    import json
except ImportError:
    import simplejson as json
    
import os
import boto
import boto.connection
from roboto.requests.awsqueryrequest import AWSQueryRequest

class RobotoAWSQueryConnection(boto.connection.AWSQueryConnection):

    def __init__(self, service, **kwargs):
        self.service = service
        self.APIVersion = self.service.api_version
        boto.connection.AWSQueryConnection.__init__(self, **kwargs)

    def _required_auth_capability(self):
        return [self.service.authentication]
        
class AWSQueryService(object):

    def __init__(self, provider, service_name):
        self.provider = provider
        self.name = service_name
        self.connection = None
        self._get_json_dir()
        self._load_service_json()

    def connect(self, **args):
        region_name = args.get('region_name', self.regions[0]['name'])
        for region in self.regions:
            if region['name'] == region_name:
                args['host'] = region['endpoint']
        args['path'] = self.path
        args['port'] = self.port
        return RobotoAWSQueryConnection(self, **args)

    def _get_json_dir(self):
        if boto.config.has_section('roboto'):
            if boto.config.has_option('roboto', 'json_dir'):
                self.json_dir = boto.config.get_value('roboto', 'json_dir')
                self.json_dir = os.path.expanduser(self.json_dir)
                self.json_dir = os.path.expandvars(self.json_dir)
        else:
            raise ValueError('No value for json_dir found in boto config')

    def _load_service_json(self):
        json_path = os.path.join(self.json_dir, self.provider)
        json_path = os.path.join(json_path, self.name+'.json')
        if os.path.isfile(json_path):
            fp = open(json_path)
            s = fp.read()
            fp.close()
            self._schema = json.loads(s)
        else:
            print 'Unable to find service: %s' % self.name

    @property
    def api_version(self):
        return self._schema.get('api_version', None)

    @property
    def authentication(self):
        return self._schema.get('authentication', None)

    @property
    def description(self):
        return self._schema.get('description', None)
            
    @property
    def path(self):
        return self._schema.get('path', '/')
        
    @property
    def port(self):
        return self._schema.get('port', 443)

    @property
    def regions(self):
        return self._schema.get('regions', None)

    def create_request(self, request_name):
        return AWSQueryRequest(self, request_name)
    

def get_request(service_name, request_name):
    s = AWSQueryService('aws', service_name)
    r = s.create_request(request_name)
    return r
