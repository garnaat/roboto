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
"""
"""
from boto.requests.awsqueryrequest import *

class DescribeAddresses(AWSQueryRequest):
    """
    Lists elastic IP addresses assigned to your account or provides
    information about a specific address.
    """
    Params = [
        StringListParam(name='PublicIp.%d', py_name='public_ip',
                        required=False,
                        doc='Elastic IP addresses to describe.')]

    Filters = [
        StringParam(name='instance-id', py_name='instance_id',
                    doc='Instance the address is associated with (if any)'),
        StringParam(name='public-ip', py_name='public_ip',
                    doc='The elastic IP address.')]

    Returns = ['addressesSet', 'item']




            


    

