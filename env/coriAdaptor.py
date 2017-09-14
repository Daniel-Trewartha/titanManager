import os, subprocess, datetime
import src.stringUtilities as stringUtilities
import abc
from systemAdaptor import systemAdaptor

class coriAdaptor(systemAdaptor):

	#Conda stores virtual environments in conda directory - just need a name
	@property
	def activateVirtualEnv(self):
		return "source activate titanManager"

	@property
	def deactivateVirtualEnv(self):
		return "source deactivate titanManager"

	#Store the database in the env folder
	@property
	def localDBFile(self):
		return os.path.split(os.path.abspath(__file__))[0]+"/manager.db"

	#job status manager stored in main folder
	@property
	def jobStatusManagerPath(self):
		return os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..','jobStatusManager.py'))

	#Environment variable gives the current user
	@property
	def user(self):
		return os.environ['USER']

	#Environment variable that stores the scratch dir for current user
	@property
	def exampleWorkDir(self):
		return os.environ['SCRATCH']

	@property
	def totalNodes(self):
		return 9688

	#Receive a list of job objects from campaign in joblist
	#Construct a queue submission script
	#nodesAttr, wtAttr, execAttr are the job properties that give required nodes, wall time, execution command
	#startStat and endStat are the statuses job is updated to when script starts and finishes respectively
	#file suffix is appended to submission script names
	def constructSubmissionScript(self, Session, campaign, jobList, nodesAttr, wtAttr, execAttr, startStat='', endStat='', fileSuffix=''):
        scriptName = os.path.join(campaign.workDir,campaign.name+fileSuffix+".bash")
        confName = os.path.join(campaign.workDir,campaign.name+fileSuffix+".conf")
        nodes = 0
        for j in jobList:
            nodes += int(getattr(j,nodesAttr))
        with open(confName,'w') as script:
            nodesListed = 0
            for i,j in enumerate(jobList):
                if (j.nodes == 1):
                    script.write(str(nodesListed)+' '+getattr(j,execAttr)+'\n')
                else:    
                    script.write(str(nodesListed)+'-'+str(nodesListed+int(getattr(j,nodesAttr))-1)+' '+getattr(j,execAttr)+'\n')
                nodesListed += int(getattr(j,nodesAttr))
        with open(scriptName,'w') as script:
            script.write("#! /bin/bash \n")
            script.write("#SBATCH -J "+campaign.name+"\n")
            if(campaign.wallTime):
                script.write("#SBATCH -t "+str(campaign.wallTime)+"\n")
            else: 
                maxWT = parseTimeString("00:00:10")
                for j in jobList:
                    if ((getattr(j,wtAttr) is not None) and getattr(j,wtAttr) > maxWT):
                        maxWT = getattr(j,wtAttr)
                script.write("#SBATCH -t "+str(maxWT)+"\n")
            script.write("#SBATCH -N "+str(nodes)+"\n")

            script.write(campaign.header+"\n")

            if (startStat is not ''):
	            script.write(self.activateVirtualEnv+"\n")
    	        updateString = "python "+self.jobStatusManagerPath+" updateJobStatus '"
        	    for j in jobList:
            	    updateString += str(j.id)+" "
            	updateString += "' "+startStat+"\n"
            	script.write(updateString)
            	script.write(self.deactivateVirtualEnv+"\n")
            script.write('srun --ntasks-per-node=1 -n '+str(nodes)+' --multi-prog '+confName+' \n')

            script.write(str(campaign.footer)+"\n")

            if (endStat is not ''):
	            script.write(self.activateVirtualEnvPath+"\n")
    	        updateString = "python "+self.jobStatusManagerPath+" updateJobStatus '"
        	    for j in jobList:
            	    updateString += str(j.id)+" "
            	updateString += "' "+endStat+"\n"
            	script.write(updateString)
            	script.write(self.deactivateVirtualEnv+"\n")
        return scriptName

    def getFreeResources(self):
    	cmd = "squeue -a | grep ' R '"
		qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
		freeNodes = int(self.totalNodes)
		minWallTime = datetime.timedelta(hours=3000)
		for line in str.split(qstatOut,'\n'):
			sLine = str.split(line)
			if (len(sLine) == 8):
				if(int(sLine[6])):
					freeNodes -= int(sLine[6])
				wallTime = stringUtilities.parseTimeString(str.split(line)[5])
				if (wallTime < minWallTime and wallTime.total_seconds() > 0):
					minWallTime = wallTime
		return freeNodes, minWallTime

	def getQueuedJobs(self):
		cmd = "squeue -u "+self.user
		qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
		queuedStats = ['Q','H','R','S']
		queuedJobs = 0
		for line in str.split(qstatOut,'\n'):
			splLine = str.split(line)
			if (len(splLine) == 8 and splLine[3] == self.user):
				if splLine[4] in queuedStats:
					queuedJobs += 1
		return queuedJobs

	def getJobStatuses(self):
		cmd = "squeue -u "+self.user
		qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
		jobsDict = {}
		for line in str.split(qstatOut,'\n'):
			splLine = str.split(line)
			if (len(splLine) == 8 and splLine[3] == self.user):
				jobsDict[splLine[0]] = splLine[4]
		return jobsDict


    def setup(self):
    	raise NotImplementedError