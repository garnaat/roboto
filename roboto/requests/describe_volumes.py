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
from boto.requests.awsqueryrequest import AWSQueryRequest
from boto.requests.params import *

class DescribeVolumes(AWSQueryRequest):
    """
    Lists elastic IP addresses assigned to your account or provides
    information about a specific address.
    """
    Params = [
        StringListParam(name='InstanceId.%d', py_name='instance_id',
                        required=False,
                        doc='Instance IDs to describe.')]

    Filters = [
        DateTimeParam(name='attachement.attach-time',
                      doc='Time stamp when the attachment initiated'),
        BooleanParam(name='attachment.delete-on-termination',
                     doc='Whether the volume will be deleted on instance \
                     termination'),
        StringParam(name='attachement.device',
                    doc='How the volume is exposed to the instance \
                    (e.g., /dev/sda1)'),
        StringParam(name='attachment.instance-id',
                    doc='ID of the instance the volume is attached to'),
        StringParam(name='attachment.status',
                    doc='Attachment state',
                    choices=('attaching', 'attached', 'detaching', 'detached')),
        StringParam(name='availability-zone',
                    doc='Availability Zone in which the volume was created'),
        DateTimeParam(name='create-time',
                      doc='Time stamp when the volume was created'),
        IntegerParam(name='size',
                     doc='Size of the volume, in GiB (e.g., 20)'),
        StringParam(name='snapshot-id',
                    doc='Snapshot from which the volume was created'),
        StringParam(name='status',
                    doc='Status of the volume',
                    choices=('creating', 'available', 'in-use',
                             'deleting', 'deleted', 'error')),
        StringParam(name='tag-key',
                    doc='Key of a tag assigned to the resource'),
        StringParam(name='tag-value',
                    doc='Value of a tag assigned to the resource'),
        StringParam(name='tag:key',
                    doc='Filters the results based on a specific tag/value \
                    combination'),
        StringParam(name='volume-id',
                    doc='Volume ID')]
    
    Returns = ['volumeSet', 'item']




            


    

