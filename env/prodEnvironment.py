import os,sys

localDBFile = os.path.split(os.path.abspath(__file__))[0]+"/manager.db"
virtualEnvPath = os.path.join('/ccs/home/danieltr/titanManager',"titanManager","bin","activate")
jobStatusManagerPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..','jobStatusManager.py'))
envVarsPath = os.path.split(os.path.abspath(__file__))[0]
totalNodes = "18649"
envName = 'environment.py'
	
with open(os.path.join(envVarsPath,envName),'w') as envFile:
	envFile.write("localDBFile=\"" + localDBFile+"\"\n")
	envFile.write("virtualEnvPath=\"" + virtualEnvPath+"\"\n")
	envFile.write("totalNodes=\"" + totalNodes+"\"\n")
	envFile.write("jobStatusManagerPath =\"" + jobStatusManagerPath + "\"\n")