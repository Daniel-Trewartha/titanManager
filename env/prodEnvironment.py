import os,sys,datetime

#Where the database is stored
localDBFile = os.path.split(os.path.abspath(__file__))[0]+"/manager.db"
#The virtualenv with required python packages
virtualEnvPath = "activate titanManager"
#The executable that updates job statuses
jobStatusManagerPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..','jobStatusManager.py'))
#Total nodes available
totalNodes = "18649"
backfillMode = False
#Maximum jobs that should be submitted to PBS at any given time
maxJobs = 50
#Maximum time any single job should run
maxWallTime = datetime.timedelta(hours=23)
#username - needed for parsing qstat data
userName = os.environ['USER']
#Project - for building submission scripts - deprecated on nersc
projectCode = 'NPH103'
maxJobFails = 5

envVarsPath = os.path.split(os.path.abspath(__file__))[0]
envName = 'environment.py'

with open(os.path.join(envVarsPath,envName),'w') as envFile:
	envFile.write("localDBFile=\"" + localDBFile+"\"\n")
	envFile.write("virtualEnvPath=\"" + virtualEnvPath+"\"\n")
	envFile.write("totalNodes=\"" + totalNodes+"\"\n")
	envFile.write("jobStatusManagerPath =\"" + jobStatusManagerPath + "\"\n")
	envFile.write("backfillMode =\"" + str(backfillMode) + "\"\n")
	envFile.write("maxJobs =\"" + str(maxJobs) + "\"\n")
	envFile.write("maxWallTime =\"" + str(maxWallTime) + "\"\n")
	envFile.write("userName =\""+userName+"\"\n")
	envFile.write("projectCode =\""+projectCode+"\"\n")