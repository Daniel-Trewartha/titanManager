import sys, os, subprocess, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
import src.stringUtilities as stringUtilities
import abc
from systemAdaptor import systemAdaptor

class titanAdaptor(systemAdaptor):

    #Conda stores virtual environments in conda directory - just need a name
    @property
    def activateVirtualEnv(self):
        return "source "+os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..','titanManager','bin','activate'))

    @property
    def deactivateVirtualEnv(self):
        return "deactivate"

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
        return os.path.join("/lustre/atlas/scratch/",self.user,self.projectCode.lower())

    #Header for the example campaign
    @property
    def exampleCampaignHeader(self):
        return "module load wraprun \ncd "+self.exampleWorkDir

    @property
    def totalNodes(self):
        return 9688

    @property
    def submitCommand(self):
        return 'qsub'

    @property
    def projectCode(self):
        return 'NPH103'

    #Get these properties from config file - implementation defined in systemAdaptor abstract class

    @property
    def maxWallTime(self):
        return super(titanAdaptor,self).maxWallTime

    @property
    def maxJobs(self):
        return super(titanAdaptor,self).maxJobs

    @property
    def maxJobFails(self):
        return super(titanAdaptor,self).maxJobFails

    @property
    def backfillMode(self):
        return super(titanAdaptor,self).backfillMode

    #Receive a list of job objects from campaign in joblist
    #Construct a queue submission script
    #nodesAttr, wtAttr, execAttr are the job properties that give required nodes, wall time, execution command
    #startStat and endStat are the statuses job is updated to when script starts and finishes respectively
    #file suffix is appended to submission script names
    def createSubmissionScript(self, Session, campaign, jobList, nodesAttr, wtAttr, execAttr, startStat='', endStat='', fileSuffix=''):
        scriptName = os.path.join(campaign.workDir,campaign.name+".csh")
        nodes = 0
        wraprun = 'wraprun '
        for j in jobList:
            nodes += int(getattr(j,nodesAttr))
            wraprun += '-n '+str(getattr(j,nodesAttr))
            wraprun += ' '+getattr(j,execAttr)+' : '
        wraprun = wraprun[:-2]
        with open(scriptName,'w') as script:
            script.write("#PBS -A "+self.projectCode+"\n")
            script.write("#PBS -N "+campaign.name+"\n")
            if(campaign.wallTime):
                script.write("#PBS -l walltime="+str(campaign.wallTime)+"\n")
            else: 
                maxWT = parseTimeString("00:00:10")
                for j in jobList:
                    if (((getattr(j,wtAttr) is not None) and (getattr(j,wtAttr) > maxWT))):
                        maxWT = j.wallTime
                script.write("#PBS -l walltime="+str(maxWT)+"\n")
            script.write("#PBS -l nodes="+str(nodes)+"\n")
            script.write("#PBS -j oe \n")

            script.write(campaign.header+"\n")

            if (startStat is not ''):
                script.write(self.activateVirtualEnv+"\n")
                updateString = "python "+self.jobStatusManagerPath+" updateJobStatus '"
                for j in jobList:
                    updateString += str(j.id)+" "
                updateString += "' "+startStat+"\n"
                script.write(updateString)
                script.write("deactivate\n")
            script.write(wraprun+"\n")
            script.write(str(campaign.footer)+"\n")
            
            if (endStat is not ''):
                script.write(self.activateVirtualEnv+"\n")
                updateString = "python "+self.jobStatusManagerPath+" updateJobStatus '"
                for j in jobList:
                    updateString += str(j.id)+" "
                updateString += "' "+endStat+"\n"
                script.write(updateString)
                script.write("deactivate\n")
        return scriptName


    #Get free nodes, minimum walltime on running jobs
    def getFreeResources(self):
        cmd = "qstat -a | grep ' R '"
        qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
        freeNodes = int(self.totalNodes)
        minWallTime = datetime.timedelta(hours=3000)
        for line in str.split(qstatOut,'\n'):
            sLine = str.split(line)
            if (len(sLine) == 11):
                if(int(sLine[5])):
                    freeNodes -= int(sLine[5])
                wallTime = stringUtilities.parseTimeString(str.split(line)[8]) - stringUtilities.parseTimeString(str.split(line)[10])
                if (wallTime < minWallTime and wallTime.total_seconds() > 0):
                    minWallTime = wallTime
        return freeNodes, minWallTime

    #Return a list of all jobs in queue owned by user
    def getQueuedJobs(self):
        cmd = "qstat -u "+self.user
        qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
        queuedStats = ['Q','H','R','S']
        queuedJobs = 0
        for line in str.split(qstatOut,'\n'):
            splLine = str.split(line)
            if (len(splLine) == 11 and splLine[1] == self.user):
                if splLine[9] in queuedStats:
                    queuedJobs += 1
        return queuedJobs

    #Return a dict of jobs owned by user with their status
    def getJobStatuses(self):
        cmd = "qstat -u "+self.user
        qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
        jobsDict = {}
        for line in str.split(qstatOut,'\n'):
            splLine = str.split(line)
            if (len(splLine) == 11 and splLine[1] == self.user):
                jobsDict[splLine[0]] = splLine[9]
        return jobsDict

    def setup(self):
        requirementsFile = os.path.join(os.path.split(os.path.abspath(__file__))[0],"requirements.txt")

        reqsList = ["asn1crypto==0.22.0","bcrypt==3.1.3","certifi==2017.7.27.1","cffi==1.10.0","chardet==3.0.4","click==6.7","cryptography==2.0.3","enum34==1.1.6",
                    "Faker==0.7.15","Flask==0.12.2","globus-sdk==1.1.1","idna==2.6","ipaddress==1.0.18","itsdangerous==0.24","Jinja2==2.9.6","MarkupSafe==1.0",
                    "paramiko==2.2.1","pyasn1==0.3.3","pycparser==2.18","PyNaCl==1.1.2","python-dateutil==2.6.0","requests==2.18.4","six==1.10.0","SQLAlchemy==1.1.10",
                    "urllib3==1.22","Werkzeug==0.12.2"]

        with open(requirementsFile,'w') as f:
            for r in reqsList:
                f.write(r+"\n")

        setupScript = os.path.join(os.path.split(os.path.abspath(__file__))[0],"titanSetup.bash")
        with open(setupScript,'w') as f:
            f.write("#! /bin/bash \n")
            f.write("module load python \n")
            f.write("module load python_setuptools \n")
            f.write("module load python_virtualenv \n")
            f.write("virtualenv titanManager \n")
            f.write(self.activateVirtualEnv+"\n")
            f.write("pip install -r "+requirementsFile+" \n")
            f.write("easy_install faker \n")

        return setupScript
