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
from roboto import mklist

class Param:

    def __init__(self, name, py_name=None, short_name=None, long_name=None,
                 required=False, default=None, doc='', choices=None):
        self.name = name
        self.py_name = py_name
        self.long_name = long_name
        self.short_name = short_name
        self.required = required
        self.default = default
        self.doc = doc
        self.choices = choices

    def encode(self, d, v, **kwargs):
        pass

class StringParam(Param):

    def encode(self, d, v, label=None):
        if not label:
            label = self.name
        d[label] = v

class StringListParam(Param):
    
    def encode(self, d, v, label=None):
        if not label:
            label = self.name
        for i, value in enumerate(mklist(v)):
            d[label%(i+1)] = value

class IntegerParam(Param):

    def encode(self, d, v, label=None):
        if not label:
            label = self.name
        d[label] = '%d' % v

class BooleanParam(Param):

    def encode(self, d, v, label=None):
        if not label:
            label = self.name
        if v:
            v = 'true'
        else:
            v = 'false'
        d[label] = v

class DateTimeParam(Param):

    def encode(self, d, v, label=None):
        if not label:
            label = self.name
        d[label] = v

