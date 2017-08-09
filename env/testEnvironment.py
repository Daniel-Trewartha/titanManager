import os,sys,datetime

#An environment for running tests

localDBFile = os.path.split(os.path.abspath(__file__))[0]+"/test.db"
virtualEnvPath = os.path.join('/ccs/home/danieltr/titanManager',"titanManager","bin","activate")
jobStatusManagerPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..','jobStatusManager.py'))
envVarsPath = os.path.split(os.path.abspath(__file__))[0]
totalNodes = "18649"
envName = 'environment.py'
backfillMode = False
maxJobs = 10
maxWallTime = datetime.timedelta(hours=1)
maxJobFails = 1
maxStageIns = 1
userName = 'danieltr'
projectCode = 'NPH103'
cluster = 'titan'

with open(os.path.join(envVarsPath,envName),'w') as envFile:
	envFile.write("localDBFile=\"" + localDBFile+"\"\n")
	envFile.write("virtualEnvPath=\"" + virtualEnvPath+"\"\n")
	envFile.write("totalNodes=\"" + totalNodes+"\"\n")
	envFile.write("jobStatusManagerPath =\"" + jobStatusManagerPath + "\"\n")
	envFile.write("backfillMode =\"" + str(backfillMode) + "\"\n")
	envFile.write("maxJobs =\"" + str(maxJobs) + "\"\n")
	envFile.write("maxWallTime =\"" + str(maxWallTime) + "\"\n")
	envFile.write("maxJobFails =\"" + str(maxJobFails) + "\"\n")
	envFile.write("maxStageIns =\"" + str(maxStageIns) + "\"\n")
	envFile.write("userName =\""+userName+"\"\n")
	envFile.write("projectCode =\""+projectCode+"\"\n")
	envFile.write("cluster =\""+cluster+"\"\n")