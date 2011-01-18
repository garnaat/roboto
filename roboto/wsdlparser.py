# Copyright (c) 2010-2011 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2010-2011, Eucalyptus Systems, Inc.
# All rights reserved.
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

import xml.dom.minidom
import sys
import re
import copy
import os
import json
from roboto import pythonize_name

class WSDLParser(object):
    
    WSDL_NS = 'http://schemas.xmlsoap.org/wsdl/'
    XS_NS = 'http://www.w3.org/2001/XMLSchema'
    SOAP_NS = 'http://schemas.xmlsoap.org/wsdl/soap/'
    TNS_NS = 'https://iam.amazonaws.com/doc/2010-05-08/'

    BaseTypes = ['string', 'integer', 'enum', 'boolean']

    def __init__(self, wsdl_file_path):
        self.service = {}
        self.types = {}
        self.messages = {}
        self.doc = xml.dom.minidom.parse(wsdl_file_path)
        self.doc_re = re.compile('<[^>]*>')
        self.parse()

    def try_element(self, parent, ns, element_name, exit_on_error=False):
        try:
            nodes = parent.getElementsByTagNameNS(ns, element_name)
            if not nodes:
                nodes = parent.getElementsByTagName(element_name)
            return nodes[0]
        except IndexError:
            if exit_on_error:
                print 'Service element not found in WSDL'
                sys.exit(1)
            else:
                return None

    def _parse_documentation(self, elem, dict):
        for child in elem.childNodes:
            if child.nodeType == elem.ELEMENT_NODE:
                if child.tagName == 'xs:annotation':
                    doc = self.try_element(child, self.XS_NS, 'documentation')
                    if doc:
                        s = doc.firstChild.data
                        s = self.doc_re.sub('', s)
                        l = s.split('\n')
                        l = [s.strip() for s in l]
                        dict['doc'] = ' '.join(l)
            
    def _parse_simple_type(self, type_elem, type_dict):
        #type_dict['name'] = type_elem.getAttribute('name')
        restriction = self.try_element(type_elem, self.XS_NS, 'restriction')
        if restriction:
            type = restriction.getAttribute('base')
            type_dict['type'] = type.split(':')[-1]
            for child in restriction.childNodes:
                if child.nodeType == type_elem.ELEMENT_NODE:
                    if child.tagName == 'xs:pattern':
                        type_dict['pattern'] = child.getAttribute('value')
                    elif child.tagName == 'xs:minLength':
                        val = child.getAttribute('value')
                        try:
                            val = int(val)
                        except:
                            pass
                        type_dict['min_length'] = val
                    elif child.tagName == 'xs:maxLength':
                        val = child.getAttribute('value')
                        try:
                            val = int(val)
                        except:
                            pass
                        type_dict['max_length'] = val
                    elif child.tagName == 'xs:enumeration':
                        type_dict['type'] = 'enum'
                        if 'choices' not in type_dict:
                            type_dict['choices'] = [child.getAttribute('value')]
                        else:
                            type_dict['choices'].append(child.getAttribute('value'))
                    else:
                        print 'Unknown restriction: ', child.tagName
        else:
            type_dict['type'] = 'simple'

    def _parse_complex_type(self, type_elem, type_dict):
        name = type_elem.getAttribute('name')
        #if name:
        #    type_dict['name'] = name
        sequence = self.try_element(type_elem, self.XS_NS, 'sequence')
        prop_dict = {}
        type_dict['properties'] = prop_dict
        type_dict['type'] = 'object'
        if sequence:
            for child in sequence.childNodes:
                if child.nodeType == type_elem.ELEMENT_NODE:
                    if child.tagName == 'xs:element':
                        min_occurs = child.getAttribute('minOccurs')
                        max_occurs = child.getAttribute('maxOccurs')
                        param_dict = {}
                        prop_dict[child.getAttribute('name')] = param_dict
                        self._parse_documentation(child, param_dict)
                        type = child.getAttribute('type')
                        if not type:
                            type = child.getAttribute('ref')
                        if min_occurs == '0':
                            param_dict['optional'] = True
                        if max_occurs == 'unbounded':
                            param_dict['type'] = 'array'
                            param_dict['items'] = []
                            param_dict['items'].append({'type' : type.split(':')[-1]})
                        else:
                            param_dict['type'] = type.split(':')[-1]

    def _parse_element_type(self, type_elem, type_dict):
        type_dict['name'] = type_elem.getAttribute('name')
        type_dict['type'] = type_elem.getAttribute('type')
        ct = self.try_element(type_elem, self.XS_NS, 'complexType')
        if ct:
            self._parse_type(ct, type_dict)

    def _parse_type(self, node, type_dict):
        if node.nodeType == node.ELEMENT_NODE:
            self._parse_documentation(node, type_dict)
            if node.tagName == 'xs:element':
                self._parse_element_type(node, type_dict)
            if node.tagName == 'xs:complexType':
                self._parse_complex_type(node, type_dict)
            elif node.tagName == 'xs:simpleType':
                self._parse_simple_type(node, type_dict)
            self.types[node.getAttribute('name')] = type_dict
        
    def _parse_types(self):
        type_node = self.try_element(self.doc, self.WSDL_NS, 'types', True)
        schema_node = self.try_element(type_node, self.XS_NS, 'schema', True)
        for child in schema_node.childNodes:
            type_dict = {}
            self._parse_type(child, type_dict)

    def _parse_messages(self):
        for msg in self.doc.getElementsByTagName('message'):
            msg_name = msg.getAttribute('name')
            for part in msg.getElementsByTagName('part'):
                element_name = part.getAttribute('element').split(':')[-1]
            self.messages[msg_name] = element_name
        for msg in self.doc.getElementsByTagNameNS(self.WSDL_NS, 'message'):
            msg_name = msg.getAttribute('name')
            for part in msg.getElementsByTagNameNS(self.WSDL_NS, 'part'):
                element_name = part.getAttribute('element').split(':')[-1]
            self.messages[msg_name] = element_name

    def _parse_porttype(self, binding_type):
        for porttype in self.doc.getElementsByTagNameNS(self.WSDL_NS, 'portType'):
            if porttype.getAttribute('name') == binding_type:
                porttype_dict = {}
                porttype_dict['name'] = porttype.getAttribute('name')
                self.service['porttype'] = porttype_dict
                porttype_dict['operations'] = {}
                self._parse_documentation(porttype, porttype_dict)
                operations = porttype.getElementsByTagNameNS(self.WSDL_NS, 'operation')
                for operation in operations:
                    operation_dict = {}
                    operation_name = operation.getAttribute('name')
                    porttype_dict['operations'][operation_name] = operation_dict
                    input_msg = self.try_element(operation, self.WSDL_NS, 'input', True)
                    im = input_msg.getAttribute('message').split(':')[-1]
                    operation_dict['params'] = [self.messages[im]]
                    output_msg = self.try_element(operation, self.WSDL_NS, 'output', True)
                    om = output_msg.getAttribute('message').split(':')[-1]
                    operation_dict['response'] = [om]
                    self._parse_documentation(operation, operation_dict)
                    
    def _parse_binding(self, binding_name):
        binding = self.try_element(self.doc, self.WSDL_NS, 'binding', True)
        binding_dict = {}
        self.service['binding'] = binding_dict
        binding_dict['name'] = binding.getAttribute('name')
        type = binding.getAttribute('type').split(':')[-1]
        binding_dict['type'] = type
        return type

    def _parse_service(self):
        service = self.try_element(self.doc, self.WSDL_NS, 'service', True)
        self.service = {}
        self._parse_documentation(service, self.service)
        self.service['name'] = service.getAttribute('name')
        self.service['type'] = 'AWSQuery'
        port = self.try_element(service, self.WSDL_NS, 'port', True)
        binding_name = port.getAttribute('binding').split(':')[-1]
        return binding_name

    def parse(self):
        self._parse_types()
        self._parse_messages()
        binding_name = self._parse_service()
        binding_type = self._parse_binding(binding_name)
        self._parse_porttype(binding_type)

def find_real_type(p, type_dict):
    type_name = type_dict['type'].split(':')[-1]
    if type_name in ['string', 'boolean', 'integer', 'enum']:
        return type_dict
    if type_name == 'object':
        nd = {}
        for prop_name in type_dict['properties']:
            if 'doc' in type_dict['properties'][prop_name]:
                nd['doc'] = type_dict['properties'][prop_name]['doc']
            nd[prop_name] = find_real_type(p, type_dict['properties'][prop_name])
        type_dict['properties'] = nd
        return type_dict
    if type_name == 'array':
        nl = []
        for item in type_dict['items']:
            nl.append(find_real_type(p, item))
        type_dict['items'] = nl
        return type_dict
    d = copy.deepcopy(p.types[type_name])
    if 'doc' in type_dict:
        d['doc'] = type_dict['doc']
    return find_real_type(p, d)

def simplify_type(type_dict):
    if 'properties' in type_dict:
        if len(type_dict['properties']) == 1:
            key = type_dict['properties'].keys()[0]
            val = type_dict['properties'][key]
            del type_dict['properties']
            type_dict.update(val)
            type_dict['name'] = key
            simplify_type(type_dict)
        else:
            for prop in type_dict['properties']:
                simplify_type(type_dict['properties'][prop])
    elif 'items' in type_dict:
        for item in type_dict['items']:
            simplify_type(item)

def build_json(wsdl_file, json_dir):
    ops = []
    p = WSDLParser(wsdl_file)
    for operation in p.service['porttype']['operations']:
        op_dict = p.service['porttype']['operations'][operation]
        new_dict = {'name' : operation,
                    'params' : []}
        if 'doc' in op_dict:
            new_dict['doc'] = op_dict['doc']
        ops.append(new_dict)
        for param1 in op_dict['params']:
            short_names = []
            param_dict = copy.deepcopy(p.types[param1])
            param_type = find_real_type(p, param_dict)
            simplify_type(param_type)
            if 'properties' in param_type:
                for param2 in param_type['properties']:
                    val = param_type['properties'][param2]
                    if isinstance(val, dict):
                        val['name'] = param2
                        if 'optional' not in val:
                            val['optional'] = True
                        cli_name = pythonize_name(param2, '-')
                        i = 0
                        short_name = cli_name[0]
                        while short_name in short_names:
                            i += 1
                            short_name = cli_name[i]
                        short_names.append(short_name)
                        val['cli_option'] = [short_name, cli_name]
                        new_dict['params'].append(val)
            else:
                new_dict['params'].append(param_type)
        for response in op_dict['response']:
            resp_dict = copy.deepcopy(p.types[response])
            resp_type = find_real_type(p, resp_dict)
            simplify_type(resp_type)
            if 'properties' in resp_type:
                for param2 in resp_type['properties']:
                    val = param_type['properties'][param2]
                    if isinstance(val, dict):
                        val['name'] = param2
                        if 'optional' not in val:
                            val['optional'] = True
                        cli_name = pythonize_name(param2, '-')
                        i = 0
                        short_name = cli_name[0]
                        while short_name in short_names:
                            i += 1
                            short_name = cli_name[i]
                        short_names.append(short_name)
                        val['cli_option'] = [short_name, cli_name]
                        new_dict['params'].append(val)
            else:
                new_dict['params'].append(param_type)
    for op in ops:
        json_filename = op['name'] + '.json'
        json_filename = os.path.join(json_dir, json_filename)
        fp = open(json_filename, 'w')
        json.dump(op, fp)
        fp.close()
        print 'Wrote file: %s' % json_filename
    return ops

