import sys, os, subprocess, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
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

    #Header for the example campaign
    @property
    def exampleCampaignHeader(self):
        return "#SBATCH -p debug\n#SBATCH -C haswell\nmodule load python"

    @property
    def totalNodes(self):
        return 9688

    @property
    def submitCommand(self):
        return 'sbatch'

    #location of wraprun executable
    @property
    def wraprun(self):
        return  os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'wraprun','wraprun'))

    #Get these properties from config file - implementation defined in systemAdaptor abstract class

    @property
    def maxWallTime(self):
        return super(coriAdaptor,self).maxWallTime

    @property
    def maxJobs(self):
        return super(coriAdaptor,self).maxJobs

    @property
    def maxJobFails(self):
        return super(coriAdaptor,self).maxJobFails

    @property
    def backfillMode(self):
        return super(coriAdaptor,self).backfillMode

    #Receive a list of job objects from campaign in joblist
    #Construct a queue submission script
    #nodesAttr, wtAttr, execAttr are the job properties that give required nodes, wall time, execution command
    #startStat and endStat are the statuses job is updated to when script starts and finishes respectively
    #file suffix is appended to submission script names
    def createSubmissionScript(self, Session, campaign, jobList, nodesAttr, wtAttr, execAttr, startStat='', endStat='', fileSuffix=''):
        scriptName = os.path.join(campaign.workDir,campaign.name+fileSuffix+".bash")
        nodes = 0
        wraprun = self.wraprun+' '
        for j in jobList:
            nodes += int(getattr(j,nodesAttr))
            wraprun += '-n '+str(getattr(j,nodesAttr))
            wraprun += ' '+getattr(j,execAttr)+' : '
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
            script.write(wraprun+"\n")

            script.write(str(campaign.footer)+"\n")

            if (endStat is not ''):
                script.write(self.activateVirtualEnv+"\n")
                updateString = "python "+self.jobStatusManagerPath+" updateJobStatus '"
                for j in jobList:
                    updateString += str(j.id)+" "
                updateString += "' "+endStat+"\n"
                script.write(updateString)
                script.write(self.deactivateVirtualEnv+"\n")
        return scriptName

    #Get free nodes, minimum walltime on running jobs
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

    #Return a list of all jobs in queue owned by user
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

    #Return a dict of jobs owned by user with their status
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
        requirementsFile = os.path.join(os.path.split(os.path.abspath(__file__))[0],"requirements.txt")

        reqsList = ["Cheetah==2.4.4","ipaddress==1.0.18","jsonschema==2.6.0","Markdown==2.6.7","python-dateutil==2.6.0","PyYAML==3.12","pyzmq==16.0.2","requests==2.11.1","singledispatch==3.4.0.3","six==1.10.0","SQLAlchemy==1.1.10","tornado==4.5.1"]
        with open(requirementsFile,'w') as f:
            for r in reqsList:
                f.write(r+"\n")

        setupScript = os.path.join(os.path.split(os.path.abspath(__file__))[0],"coriSetup.bash")
        with open(setupScript,'w') as f:
            f.write("#! /bin/bash \n")
            f.write("module load python \n")
            f.write("conda create -n titanManager --file "+requirementsFile+"\n")

        return setupScript
