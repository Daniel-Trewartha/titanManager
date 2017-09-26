import os, sys, importlib
import ConfigParser

config = ConfigParser.ConfigParser()
configFile = os.path.join(os.path.split(os.path.abspath(__file__))[0],'config.ini')
config.read(configFile)

ad = config.get("Adaptor","adaptor")
adapt = importlib.import_module('env.'+ad)

adaptor = getattr(adapt,ad)()