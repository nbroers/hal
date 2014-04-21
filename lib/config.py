"""Application configuration

Configuration and related classes"""

import ConfigParser
import json

class Config():
    """Proxy to the ConfigParser class

    Proxy to the built-in ConfigParser class to prevent needing to pass the
    section with every request to the ConfigParser.
    """
    def __init__(self, default_configuration_file_paths,
                 configuration_file_paths, section):
        self.default = ConfigParser.SafeConfigParser()
        self.config = ConfigParser.SafeConfigParser()
        self.default.read(default_configuration_file_paths)
        self.config.read(configuration_file_paths)
        self.section = section

    def get(self, option, default=None):
        value = self._get(self.config, option, 
                          self._get(self.default, option, default))
        return value

    def getint(self, option, default=None):
        value = self._getint(self.config, option, self._getint(
                            self.default, option, default))
        return value

    def getfloat(self, option, default=None):
        value = self._getfloat(self.config, option, self._getfloat(
                            self.default, option, default))
        return value

    def _get(self, config, option, default=None):
        try:
            value = config.get(self.section, option)
            if value and value.strip()[0] + value.strip()[-1] == '[]':
                value = json.loads(value)
            return value
        except ConfigParser.NoOptionError:
            return default

    def _getint(self, config, option, default=None):
        try:
            return config.getint(self.section, option)
        except ConfigParser.NoOptionError:
            return default

    def _getfloat(self, config, option, default=None):
        try:
            return config.getfloat(self.section, option)
        except ConfigParser.NoOptionError:
            return default


