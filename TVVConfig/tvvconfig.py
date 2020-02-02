import json
from json import JSONDecoder

# Note:  this is the default location of application secrets when containered
CONFIG_FILE = "/tvv/secrets/tvvmia.settings.json"
class TVVConfigApi(JSONDecoder):
    configFile = None
    JSON = None
    def __init__(self):
        JSONDecoder.__init__(self)
        if None == self.configFile:
            self.configFile = open(CONFIG_FILE, 'r')
        if None != self.configFile:
            self.JSON = json.load(self.configFile)
        if None == self.JSON:
            print("Default config.json not found! Pursing")
    def get(self, section, name):
        if None != self.JSON:
            section_dict = self.JSON.get(section)
            if None != section_dict:
                return section_dict.get(name)
        else:
            import os
            return os.environ.get(section + '_' + name)
        return None
class TVVConfigApp(TVVConfigApi):
    def __init__(self):
        TVVConfigApi.__init__(self)
class TVVConfigAgent(TVVConfigApi):
    def __init__(self):
        TVVConfigApi.__init__(self)