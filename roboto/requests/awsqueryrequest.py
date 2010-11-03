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
from optparse import OptionParser
import boto
from boto.ec2.connection import EC2Connection
import roboto.jsonresponse
from roboto import mklist, pythonize_name

class ValidationException(Exception):

    def __init__(self, param, msg):
        self.param = param
        self.msg = msg

    def __repr__(self):
        return 'Invalid value for param %s of type %s: %s' % (param['name'],
                                                              param['type'],
                                                              msg)

class Param:

    @classmethod
    def encode(cls, p, rp, v, label=None):
        try:
            mthd = getattr(cls, 'encode_'+p['type'])
            mthd(p, rp, v, label)
        except AttributeError:
            raise 'Unknown type: %s' % p['type']
        
    @classmethod
    def encode_string(cls, p, rp, v, l):
        if l:
            label = l
        else:
            label = p['name']
        rp[label] = v

    @classmethod
    def encode_integer(cls, p, rp, v, l):
        if l:
            label = l
        else:
            label = p['name']
        rp[label] = '%d' % v
        
    @classmethod
    def encode_boolean(cls, p, rp, v, l):
        if l:
            label = l
        else:
            label = p['name']
        if v:
            v = 'true'
        else:
            v = 'false'
        rp[label] = v
        
    @classmethod
    def encode_datetime(cls, p, rp, v, l):
        if l:
            label = l
        else:
            label = p['name']
        rp[label] = v
        
    @classmethod
    def validate(cls, p, v):
        try:
            mthd = getattr(cls, 'validate_'+p['type'])
            mthd(p, v)
        except AttributeError:
            raise ValidationException(p, '')
        
    @classmethod
    def validate_string(cls, p, v):
        pass

    @classmethod
    def validate_integer(cls, p, v):
        pass
        
    @classmethod
    def validate_boolean(cls, p, v):
        if v not in ('true', 'True', 'false', 'False', True, False):
            raise 'Invalid value for a boolean param: %s' % p['name']
        
    @classmethod
    def validate_datetime(cls, p, v):
        pass
        
class AWSQueryRequest(object):
    """
    This is an abstract base class (well, it would be if Python had such a thing)
    for all requests that are based on the AWS Query interface.
    """

    JsonPath = '/Users/mitch/Projects/roboto/data/aws/ec2'
    ConnectionCls = EC2Connection
    CLITypeMap = {'string' : 'string',
                  'integer' : 'int',
                  'enum' : 'choice',
                  'datetime' : 'string',
                  'boolean' : 'string'}

    def __init__(self, request_name, **args):
        self.name = request_name
        self.args = args
        self.parser = None
        self.http_response = None
        self.aws_response = None
        self._schema = None
        self.connection = None
        self._load_json()

    def init_connection(self):
        if self.connection is None:
            if 'connection' in self.args:
                self.connection = self.args['connection']
            else:
                self.connection = self.ConnectionCls(**self.args)
        return self.connection

    def _load_json(self):
        json_path = os.path.join(self.JsonPath, self.name+'.json')
        if os.path.isfile(json_path):
            fp = open(json_path)
            s = fp.read()
            fp.close()
            self._schema = json.loads(s)
        else:
            print 'Unable to find request: %s' % self.name
            
    @property
    def status(self):
        retval = None
        if self.http_response is not None:
            retval = self.http_response.status
        return retval

    @property
    def reason(self):
        retval = None
        if self.http_response is not None:
            retval = self.http_response.reason
        return retval

    @property
    def request_id(self):
        retval = None
        if self.response is not None:
            retval = getattr(self.aws_response, 'requestId')
        return retval

    @property
    def params(self):
        retval = None
        if self._schema:
            retval = self._schema['params']
        return retval

    @property
    def filters(self):
        retval = None
        if self._schema:
            retval = self._schema['filters']
        return retval

    @property
    def response(self):
        retval = None
        if self._schema:
            retval = self._schema['response']
        return retval

    def _process_filters(self, filters, request_params):
        filter_names = [f['name'] for f in self.filters]
        unknown_filters = [f for f in filters if f not in filter_names]
        if unknown_filters:
            raise ValueError, 'Unknown filters: %s' % unknown_filters
        for i, filter in enumerate(self.filters):
            if filter['name'] in filters:
                request_params['Filter.%d.Name' % (i+1)] = filter['name']
                for j, value in enumerate(mklist(filters[filter['name']])):
                    Param.encode(filter, request_params, value,
                                 'Filter.%d.Value.%d' % (i+1,j+1))

    def process_args(self, args):
        self.request_params = {}
        required = [p['name'] for p in self.params if not p['optional']]
        for param in self.params:
            if 'cli_option' in param:
                python_name = param['cli_option'][1]
            else:
                python_name = pythonize_name(param['name'])
            if python_name in args:
                if param['name'] in required:
                    required.remove(param['name'])
                value = args[python_name]
                if value is not None:
                    Param.encode(param, self.request_params, args[python_name])
                del args[python_name]
        if required:
            raise ValueError, 'Required parameters missing: %s' % required
        print 'request_params', self.request_params
        if 'filters' in args:
            self._process_filters(args['filters'], self.request_params)
            del args['filters']

    def send(self, path='/', verb='GET'):
        self.init_connection()
        self.http_response = self.connection.make_request(self.name,
                                                          self.request_params,
                                                          path, verb)
        self.body = self.http_response.read()
        boto.log.debug(self.body)
        if self.http_response.status == 200:
            self.aws_response = roboto.jsonresponse.Element()
            h = roboto.jsonresponse.XmlHandler(self.aws_response, self.connection)
            h.parse(self.body)
            return self.aws_response
        else:
            boto.log.error('%s %s' % (self.status, self.reason))
            boto.log.error('%s' % self.body)
            raise self.connection.ResponseError(self.status,
                                                self.reason,
                                                self.body)

    def build_cli_parser(self):
        self.parser = OptionParser()
        self.parser.add_option('-D', '--debug', action='store_true',
                               help='Turn on all debugging output')
        for param in self.params:
            if 'cli_option' in param:
                print 'param=', param
                short_name = '-' + param['cli_option'][0]
                long_name = '--' + param['cli_option'][1]
                type = self.CLITypeMap[param['type']]
                self.parser.add_option(short_name, long_name, action='store',
                                       type=type, help=param['doc'])

    def do_cli(self, cli_args=None):
        if not self.parser:
            self.build_cli_parser()
        options, args = self.parser.parse_args(cli_args)
        d = {}
        for param in self.params:
            if 'cli_option' in param:
                p_name = param['cli_option'][1]
                d[p_name] = getattr(options, p_name)
        self.process_args(d)
        try:
            if options.debug:
                boto.set_stream_logger(self.name)
                self.args['debug'] = 2
            self.send()
            print self.aws_response
        except self.connection.ResponseError as err:
            print 'Error(%s): %s' % (err.error_code, err.error_message)
