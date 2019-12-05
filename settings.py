import json
from json import JSONDecoder

# Note:  this is the default location of application secrets when containered
CONFIG_FILE = "/tvv/secrets/tvvmiaenterprise.settings.json"
class TVVConfigApi(JSONDecoder):
    JSON = None
    def __init__(self):
        JSONDecoder.__init__(self)
        configFile = open(CONFIG_FILE, 'r')
        self.JSON = json.load(configFile)
    def get(self, section, name):
        section_dict = self.JSON.get(section)
        if None != section_dict:
            value = section_dict.get(name)
            return value
        return None

class TVVConfigApp(TVVConfigApi):
    def __init__(self):
        TVVConfigApi.__init__(self)
        
class TVVConfigAgent(TVVConfigApi):
    def __init__(self):
        TVVConfigApi.__init__(self)