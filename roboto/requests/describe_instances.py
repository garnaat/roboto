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

class DescribeInstances(AWSQueryRequest):
    """
    Lists elastic IP addresses assigned to your account or provides
    information about a specific address.
    """
    Params = [
        StringListParam(name='InstanceId.%d', py_name='instance_id',
                        required=False,
                        doc='Instance IDs to describe.')]

    Filters = [
        StringParam(name='architecture',
                    doc='Instance architecture',
                    choices=('i386', 'x86_64')),
        StringParam(name='availability-zone',
                    doc="Instance's Availability Zone"),
        DateTimeParam(name='block-device-mapping.attach-time',
                      doc='Attach time for an Amazon EBS volume'),
        BooleanParam(name='block-device-mapping.delete-on-termination',
                     doc='Whether the Amazon EBS volume is deleted on \
                     instance termination'),
        StringParam(name='block-device-mapping.device-name',
                    doc='Device name for an Amazon EBS volume mapped to \
                    the instance'),
        StringParam(name='block-device-mapping.status',
                    doc='Status for an Amazon EBS volume mapped to the \
                    instance',
                    choices=('attaching', 'attached', 'detaching', 'detached')),
        StringParam(name='block-device-mapping.volume-id',
                    doc='ID for an Amazon EBS volume mapped to the instance'),
        StringParam(name='client-token',
                    doc='Idempotency token you provided when you launched \
                    the instance'),
        StringParam(name='dns-name',
                    doc='Public DNS name of the instance'),
        StringParam(name='group-id',
                    doc='A security group the instance is in'),
        StringParam(name='image-id',
                    doc='ID of the image used to launch the instance'),
        StringParam(name='instance-id',
                    doc='ID of the instance'),
        StringParam(name='instance-lifecycle',
                    doc='Whether this is a Spot Instance',
                    choices=('spot',)),
        IntegerParam(name='instance-state-code',
                     doc="Code identifying the instance's state",
                     choices=(0, 16, 32, 48, 64, 80)),
        StringParam(name='instance-state-name',
                    doc="Instance's state",
                    choices=('pending', 'running', 'shutting-down',
                             'terminated', 'stopping', 'stopped')),
        StringParam(name='instance-type',
                    doc='Type of instance (e.g., m1.small)'),
        StringParam(name='ip-address',
                    doc='Public IP address of the instance'),
        StringParam(name='kernel-id',
                    doc='Kernel ID'),
        StringParam(name='key-name',
                    doc='Name of the key pair used when the instance was \
                    launched'),
        StringParam(name='launch-index',
                    doc='The index for the instance in the launch group'),
        DateTimeParam(name='launch-time',
                      doc='Time instance was launched'),
        StringParam(name='monitoring-state',
                    doc='Whether monitoring is enabled for the instance',
                    choices=('disabled', 'enabled')),
        StringParam(name='owner-id',
                    doc='AWS account ID of the instance owner'),
        StringParam(name='placement-group-name',
                    doc='Name of the placement group the instance is in'),
        StringParam(name='platform',
                    doc='Use windows if you have Windows based instances; \
                    otherwise, leave blank',
                    choices=('windows',)),
        StringParam(name='private-dns-name',
                    doc='Private DNS name of the instance'),
        StringParam(name='private-ip-address',
                    doc='Private IP address of the instance'),
        StringParam(name='product-code',
                    doc='Product code associated with the AMI used to launch \
                    the instance'),
        StringParam(name='ramdisk-id',
                    doc='RAM disk ID'),
        StringParam(name='reason',
                    doc="Reason for the instance's current state"),
        StringParam(name='requester-id',
                    doc='ID of the entity that launched the instance on your \
                    behalf'),
        StringParam(name='reservation-id',
                    doc="ID of the instance's reservation"),
        StringParam(name='root-device-name',
                    doc='Root device name of the instance (e.g., /dev/sda1)'),
        StringParam(name='root-device-type',
                    doc='Root device type the instance uses',
                    choices=('ebs', 'instance-store')),
        StringParam('spot-instance-request-id',
                    doc='ID of the Spot Instance request'),
        StringParam(name='state-reason-code',
                    doc='Reason code for the state change'),
        StringParam(name='state-reason-message',
                    doc='Message for the state change'),
        StringParam(name='subnet-id',
                    doc='ID of the subnet the instance is in (if using VPC)'),
        StringParam(name='tag-key',
                    doc='Key of a tag assigned to the resource'),
        StringParam(name='tag-value',
                    doc='Value of a tag assigned to the resource'),
        StringParam(name='tag:key',
                    doc='Filters the results based on a specific tag/value \
                    combination'),
        StringParam(name='virtualization-type',
                    doc='Virtualization type of the instance',
                    choices=('paravirtual', 'hvm')),
        StringParam(name='vpc-id',
                    doc='ID of the VPC the instance is in (if using \
                    Amazon VPC)')]
    
    Returns = ['reservationSet', 'item']




            


    

