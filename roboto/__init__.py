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

import boto.utils

class Param:

    @classmethod
    def encode(cls, p, rp, v, label=None):
        try:
            mthd = getattr(cls, 'encode_'+p.type)
            mthd(p, rp, v, label)
        except AttributeError:
            raise 'Unknown type: %s' % p.type
        
    @classmethod
    def encode_string(cls, p, rp, v, l):
        if l:
            label = l
        else:
            label = boto.utils.awsify_name(p.name)
        rp[label] = v

    @classmethod
    def encode_integer(cls, p, rp, v, l):
        if l:
            label = l
        else:
            label = boto.utils.awsify_name(p.name)
        rp[label] = '%d' % v
        
    @classmethod
    def encode_boolean(cls, p, rp, v, l):
        if l:
            label = l
        else:
            label = boto.utils.awsify_name(p.name)
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
            label = boto.utils.awsify_name(p.name)
        rp[label] = v
        
    @classmethod
    def encode_array(cls, p, rp, v, l):
        v = boto.utils.mklist(v)
        if l:
            label = l
        else:
            label = boto.utils.awsify_name(p.name)
        label = label + '.%d'
        for i, value in enumerate(v):
            rp[label%(i+1)] = value
        
    @classmethod
    def validate(cls, p, v):
        try:
            mthd = getattr(cls, 'validate_'+p.type)
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
            raise 'Invalid value for a boolean param: %s' % p.name
        
    @classmethod
    def validate_datetime(cls, p, v):
        pass
        
