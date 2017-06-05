import os

os.environ["localDBFile"] = os.path.split(os.path.abspath(__file__))[0]+"/manager.db"
os.environ["virtualEnvPath"] = os.path.join(os.path.split(os.path.abspath(__file__))[0],"titanManager","bin","activate")
os.environ["envVarsPath"] = os.path.abspath(__file__)
os.environ["totalNodes"] = "18649"
