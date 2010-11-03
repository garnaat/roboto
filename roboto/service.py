import boto
from boto.utils import find_class
from boto.regioninfo import RegionInfo

class Registry(object):

    _registry = {}

    def register(cls, svc_name, svc_data):
        self._registry[svc_name] = svc_data

    def lookup(cls, svc_name):
        self._registry[svc_name]
        
class Service(dict):

    def __init__(self, name, **kwargs):
        self['name'] = name
        self.get_config_data()
        self.region = RegionInfo(name=self.name, endpoint=self['endpoint'])

    def get_config_data(self):
        section_name = 'ShortCut_%s' % self['name']
        if boto.config.has_section(section_name):
            for option_name in boto.config.options(section_name):
                self[option_name] = boto.config.get(section_name, option_name)

    def connect(self):
        cls = find_class(self['class'])
        self.connection = cls(
