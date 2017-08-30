import os,sys,datetime

#Where the database is stored
localDBFile = os.path.split(os.path.abspath(__file__))[0]+"/manager.db"
#The virtualenv with required python packageds
virtualEnvPath = os.path.join('/ccs/home/danieltr/titanManager',"titanManager","bin","activate")
#The executable that updates job statuses
jobStatusManagerPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..','jobStatusManager.py'))
#The executable that stages in files
fileStagerPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..','fileStager.py'))
#Total nodes available
totalNodes = "18649"
backfillMode = False
#Maximum jobs that should be submitted to PBS at any given time
maxJobs = 50
#Maximum time any single job should run
maxWallTime = datetime.timedelta(hours=23)
#Maximum number of resubmissions before a job is declared failed
maxJobFails = 5
#Maximum number of stage-in attempts before a file is declared missing
maxStageIns = 5
#username - needed for parsing qstat data
userName = 'danieltr'
#Project - for building submission scripts
projectCode = 'NPH103'
#Globus endpoint for current cluster
cluster = 'olcf#dtn_atlas'
#Local ssh key for globus
localKeyFile = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'.ssh','id_rsa.globus'))
globusUserName = "danieltrewartha"
#Directory that staged in input should go to
inputDir = os.path.split(os.path.abspath(__file__))[0]
#File that globus auth tokens should be stored in
globusRefreshTokens = os.path.join(os.path.split(os.path.abspath(__file__))[0],"refresh-tokens.json")

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
	envFile.write("maxJobFails =\"" + str(maxJobFails) + "\"\n")
	envFile.write("maxStageIns =\"" + str(maxStageIns) + "\"\n")
	envFile.write("userName =\""+userName+"\"\n")
	envFile.write("projectCode =\""+projectCode+"\"\n")
	envFile.write("cluster =\""+cluster+"\"\n")
	envFile.write("fileStagerPath = \""+fileStagerPath+"\"\n")
	envFile.write("inputDir = \""+inputDir+"\"\n")
	envFile.write("globusRefreshTokens =\""+globusRefreshTokens+"\"\n")
	envFile.write("globusUserName =\""+globusUserName+"\"\n")
	envFile.write("localKeyFile =\"" + localKeyFile + "\"\n")