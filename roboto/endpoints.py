"""
Endpoint identifiers are of the form:

    <provider>.<boto module name>.<provider region name>
    
    where:
        <provider> - The short version of the service provider name
        <boto module name> - The name of the boto module that implements
                             the service
        <provider region name> - The name of the region, as defined by
                                 the service provider
"""
import boto.utils

class Endpoint(dict):

    def __init__(self, **kwargs):
        self['provider'] = None
        self['module'] = None
        self['region'] = None
        self.update(kwargs)

    def __getattr__(self, key):
        return self[key]

    def __repr__(self):
        return '%s|%s|%s' % (self['provider'], self['module'], self['region'])

    def connect(self, **kwargs):
        connection_cls = boto.utils.find_class(self['module'],
                                               'Connection')
        return connection_cls(**kwargs)

services = [
    Endpoint(provider='aws', module='boto.s3', region=None,
             name='S3 US Standard',
             endpoint='s3.amazonaws.com', constraint=None),
    Endpoint(provider='aws', module='boto.s3', region='us-west-1',
             name='S3 US-West', endpoint='s3-us-west-1.amazonaws.com',
             constraint='us-west-1'),
    Endpoint(provider='aws', module='boto.s3', region='ap-southeast-1',
             name='S3 Asia Pacific', endpoint='s3-ap-southeast-1.amazonaws.com',
             constraint='ap-southeast-1'),
    Endpoint(provider='aws', module='boto.s3', region='eu-west-1',
             name='S3 Europe', endpoint=None,
             constraint='EU'),
    Endpoint(provider='aws', module='boto.ec2', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='ec2.us-east-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='ec2.us-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='ec2.eu-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2', region='ap-southeast-1',
             name='Asia Pacific (Singapore)',
             endpoint='ec2.ap-southeast-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sdb', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='sdb.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sdb', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='sdb.us-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sdb', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='sdb.eu-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sdb', region='ap-southest-1',
             name='Asia Pacific (Singapore)',
             endpoint='sdb.ap-southeast-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.rds', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='rds.us-east-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.rds', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='rds.us-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.rds', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='rds.eu-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.rds', region='ap-southeast-1',
             name='Asia Pacific (Singapore)',
             endpoint='rds.ap-southeast-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sqs', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='sqs.us-east-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sqs', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='sqs.us-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sqs', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='sqs.eu-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sqs', region='ap-southeast-1',
             name='Asia Pacific (Singapore)',
             endpoint='sqs.ap-southeast-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sns', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='sns.us-east-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sns', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='sns.us-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sns', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='sns.eu-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.sns', region='ap-southeast-1',
             name='Asia Pacific (Singapore)',
             endpoint='sns.ap-southeast-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.monitoring', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='monitoring.us-east-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.monitoring', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='monitoring.us-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.monitoring', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='monitoring.eu-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.monitoring', region='ap-southeast-1',
             name='Asia Pacific (Singapore)',
             endpoint='monitoring.ap-southeast-1.amazonaws.com'),
    Endpoint(provider='aws', module='cloudfront', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='cloudfront.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.autoscaling', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='autoscaling.us-east-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.autoscaling', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='autoscaling.us-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.autoscaling', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='autoscaling.eu-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.autoscaling', region='ap-southeast-1',
             name='Asia Pacific (Singapore)',
             endpoint='autoscaling.ap-southeast-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.elb', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='elasticloadbalancing.us-east-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.elb', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='elasticloadbalancing.us-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.elb', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='elasticloadbalancing.eu-west-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.ec2.elb', region='ap-southeast-1',
             name='Asia Pacific (Singapore)',
             endpoint='elasticloadbalancing.ap-southeast-1.amazonaws.com'),
    Endpoint(provider='aws', module='boto.emr', region='us-east-1',
             name='US-East (Northern Virginia)',
             endpoint='us-east-1.elasticmapreduce.amazonaws.com'),
    Endpoint(provider='aws', module='boto.emr', region='us-west-1',
             name='US-West (Northern California)',
             endpoint='us-west-1.elasticmapreduce.amazonaws.com'),
    Endpoint(provider='aws', module='boto.emr', region='eu-west-1',
             name='EU (Ireland)',
             endpoint='eu-west-1.elasticmapreduce.amazonaws.com'),
    Endpoint(provider='google', module='boto.gs', region='us',
             name='United States',
             endpoint='commondatastorage.googleapis.com'),
    ]

def search(provider=None, module=None, region=None):
    results = []
    for endpoint in services:
        candidate = endpoint
        if provider and provider != endpoint.provider:
            candidate = None
        if module and module != endpoint.module:
            candidate = None
        if region and region != endpoint.region:
            candidate = None
        if candidate:
            results.append(candidate)
    return results
