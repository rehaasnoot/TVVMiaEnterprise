import json
from json import JSONDecoder

# Note:  this is the default location of application secrets when containered
CONFIG_FILE = "/tvv/secrets/tvvmiaenterprise.config.json"
class TVVConfigApi(JSONDecoder):
    JSON = None
    def __init__(self):
        JSONDecoder.__init__(self)
        configFile = open(CONFIG_FILE, 'r')
        self.JSON = json.load(configFile)
    def get(self, section, name):
        section_dict = self.JSON.get(section)
        value = section_dict.get(name)
        return value

class TVVConfigApp(TVVConfigApi):
    def __init__(self):
        TVVConfigApi.__init__()