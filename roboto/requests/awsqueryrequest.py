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
import pdb
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

class Line(object):

    def __init__(self, fmt, data, label):
        self.fmt = fmt
        self.data = data
        self.label = label
        self.line = '%s\t' % label
        self.printed = False

    def append(self, datum):
        self.line += '%s\t' % datum

    def print_it(self):
        if not self.printed:
            print self.line
            self.printed = True
                
class AWSQueryRequest(object):
    """
    This is an abstract base class (well, it would be if Python had such a thing)
    for all requests that are based on the AWS Query interface.
    """

    JsonPath = '/Users/mitch/Projects/roboto/roboto/services/aws/ec2'
    ConnectionCls = EC2Connection
    CLITypeMap = {'string' : 'string',
                  'integer' : 'int',
                  'int' : 'int',
                  'enum' : 'choice',
                  'datetime' : 'string',
                  'boolean' : 'string'}

    def __init__(self, request_name, **args):
        self.name = request_name
        self.args = args
        self.request_params = {}
        self.list_markers = []
        self.item_markers = []
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
            self.process_markers(self.response)
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
            if hasattr(self._schema, 'filters'):
                retval = self._schema['filters']
        return retval

    @property
    def response(self):
        retval = None
        if self._schema:
            if 'response' in self._schema:
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

    def process_markers(self, fmt, prev_name=None):
        if fmt['type'] == 'object':
            for prop in fmt['properties']:
                self.process_markers(prop, fmt['name'])
        elif fmt['type'] == 'array':
            self.list_markers.append(prev_name)
            self.item_markers.append(fmt['name'])
        
    def send(self, path='/', verb='GET'):
        self.init_connection()
        self.http_response = self.connection.make_request(self.name,
                                                          self.request_params,
                                                          path, verb)
        self.body = self.http_response.read()
        boto.log.debug(self.body)
        if self.http_response.status == 200:
            self.aws_response = roboto.jsonresponse.Element(list_marker=self.list_markers,
                                                            item_marker=self.item_markers)
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
                type = self.CLITypeMap[param['type']]
                if param['cli_option'][0] is None:
                    long_name = '--' + param['cli_option'][1]
                    self.parser.add_option(long_name,
                                           action='store', type=type,
                                           help=param.get('doc', None))
                else:
                    short_name = '-' + param['cli_option'][0]
                    long_name = '--' + param['cli_option'][1]
                    self.parser.add_option(short_name, long_name,
                                           action='store', type=type,
                                           help=param.get('doc', None))

    def do_cli(self, cli_args=None):
        if not self.parser:
            self.build_cli_parser()
        options, args = self.parser.parse_args(cli_args)
        if hasattr(options, 'help_filters') and options.help_filters:
            print 'Available filters:'
            for filter in self.filters:
                print '%s\t%s' % (filter['name'], filter['doc'])
            sys.exit(0)
        d = {}
        for param in self.params:
            if 'cli_option' in param:
                p_name = param['cli_option'][1]
                d[p_name] = getattr(options, p_name.replace('-', '_'))
            else:
                p_name = pythonize_name(param['name'])
                d[p_name] = args
        self.process_args(d)
        if hasattr(options, 'filter') and options.filter:
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

    def _cli_fmt(self, fmt, data, line=None):
        if 'items' not in fmt:
            for key in fmt:
                self._cli_fmt(fmt[key], data[key], line)
        else:
            if isinstance(data, list):
                for data_item in data:
                    if 'label' in fmt:
                        if line:
                            line.print_it()
                        line = Line(fmt, data, fmt['label'])
                    for fmt_item in fmt['items']:
                        if isinstance(fmt_item, dict):
                            self._cli_fmt(fmt_item, data_item[fmt_item['name']], line)
                        else:
                            try:
                                val = data_item[fmt_item]
                                if not val:
                                    val = ''
                                line.append(val)
                            except KeyError:
                                boto.log.debug("%s not found in %s" % (fmt_item, data_item))
                    line.print_it()
                    line = None

    def _generic_cli_formatter(self, fmt, data, label=''):
        if fmt['type'] == 'object':
            for prop in fmt['properties']:
                if 'name' in fmt:
                    if fmt['name'] in data:
                        data = data[fmt['name']]
                    if fmt['name'] in self.list_markers:
                        label = fmt['name']
                        if label[-1] == 's':
                            label = label[0:-1]
                        label = label.upper()
                self._generic_cli_formatter(prop, data, label)
        elif fmt['type'] == 'array':
            for item in data:
                line = Line(fmt, item, label)
                if isinstance(item, dict):
                    for field_name in item:
                        line.append(item[field_name])
                elif isinstance(item, basestring):
                    line.append(item)
                line.print_it()

    def cli_output_formatter(self):
        if self.cli_output_format:
            self._cli_fmt(self.cli_output_format, self.aws_response)
        elif self.response:
            self._generic_cli_formatter(self.response, self.aws_response)
        else:
            print 'No formatter found: dumping raw data'
            print self.aws_response
