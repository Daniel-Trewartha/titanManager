import os, sys, importlib
import ConfigParser

config = ConfigParser.ConfigParser()
configFile = os.path.join(os.path.split(os.path.abspath(__file__))[0],'config.ini')
config.read(configFile)

ad = config.get("Adaptor","adaptor")
adapt = __import__('env.'+ad,fromlist=[''])

adaptor = getattr(adapt,ad)()