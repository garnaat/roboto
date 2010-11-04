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
    
import os, sys
from optparse import OptionParser
import boto
from boto.ec2.connection import EC2Connection
import roboto.jsonresponse
from roboto import mklist, pythonize_name, Param

class ValidationException(Exception):

    def __init__(self, param, msg):
        self.param = param
        self.msg = msg

    def __repr__(self):
        return 'Invalid value for param %s of type %s: %s' % (param['name'],
                                                              param['type'],
                                                              msg)

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
        self.request_params = {}
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

    @property
    def cli_output_format(self):
        retval = None
        if self._schema:
            if 'cli_output_format' in self._schema:
                retval = self._schema['cli_output_format']
        return retval

    def process_filters(self, args):
        filter_names = [f['name'] for f in self.filters]
        unknown_filters = [f for f in args if f not in filter_names]
        if unknown_filters:
            raise ValueError, 'Unknown filters: %s' % unknown_filters
        for i, filter in enumerate(self.filters):
            if filter['name'] in args:
                self.request_params['Filter.%d.Name' % (i+1)] = filter['name']
                for j, value in enumerate(mklist(args[filter['name']])):
                    Param.encode(filter, self.request_params, value,
                                 'Filter.%d.Value.%d' % (i+1,j+1))

    def process_args(self, args=None):
        if args:
            self.args = args
        required = [p['name'] for p in self.params if not p['optional']]
        for param in self.params:
            if 'cli_option' in param:
                python_name = param['cli_option'][1]
            else:
                python_name = pythonize_name(param['name'])
            if python_name in self.args:
                if param['name'] in required:
                    required.remove(param['name'])
                value = self.args[python_name]
                if value is not None:
                    Param.encode(param, self.request_params,
                                 self.args[python_name])
                del self.args[python_name]
        if required:
            raise ValueError, 'Required parameters missing: %s' % required
        boto.log.debug('request_params: %s' % self.request_params)

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
        if self.filters:
            self.parser.add_option('--help-filters', action='store_true',
                                   help='Display list of available filters')
            self.parser.add_option('--filter', action='append',
                                   metavar=' name=value',
                                   help='A filter for limiting the results')
        for param in self.params:
            if 'cli_option' in param:
                short_name = '-' + param['cli_option'][0]
                long_name = '--' + param['cli_option'][1]
                type = self.CLITypeMap[param['type']]
                self.parser.add_option(short_name, long_name, action='store',
                                       type=type, help=param['doc'])

    def do_cli(self, cli_args=None):
        if not self.parser:
            self.build_cli_parser()
        options, args = self.parser.parse_args(cli_args)
        if options.help_filters:
            print 'Available filters:'
            for filter in self.filters:
                print '%s\t%s' % (filter['name'], filter['doc'])
            sys.exit(0)
        d = {}
        for param in self.params:
            if 'cli_option' in param:
                p_name = param['cli_option'][1]
                d[p_name] = getattr(options, p_name)
            else:
                p_name = pythonize_name(param['name'])
                d[p_name] = args
        self.process_args(d)
        if options.filter:
            d = {}
            for filter in options.filter:
                name, value = filter.split('=')
                d[name] = value
            self.process_filters(d)
        try:
            if options.debug:
                boto.set_stream_logger(self.name)
                self.args['debug'] = 2
            self.send()
            self.cli_output_formatter()
        except self.connection.ResponseError as err:
            print 'Error(%s): %s' % (err.error_code, err.error_message)

    def _cli_fmt(self, fmt, data, line=''):
        if isinstance(data, dict):
            for key in fmt:
                d = data[key]
                f = fmt[key]
                if 'label' in f:
                    line = '%s\t' % f['label']
                self._cli_fmt(f, d, line)
        elif isinstance(data, list):
            if 'items' in fmt:
                for data_item in data:
                    if 'label' in fmt:
                        line = '%s\t' % fmt['label']
                    for fmt_item in fmt['items']:
                        if isinstance(fmt_item, dict):
                            self._cli_fmt(fmt_item, data_item[fmt_item['name']], line)
                        else:
                            line += '%s\t' % data_item[fmt_item]
                    print line
                    line = ''

    def cli_output_formatter(self):
        if self.cli_output_format:
            self._cli_fmt(self.cli_output_format, self.aws_response)
