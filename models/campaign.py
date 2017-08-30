import datetime, os, sys, subprocess, atexit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, event, ForeignKey, UniqueConstraint, orm
from sqlalchemy.orm import relationship, mapper, joinedload
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from sqlalchemy.ext.hybrid import hybrid_property
from src.base import Base
from job import Job
from env.environment import virtualEnvPath, jobStatusManagerPath, totalNodes, maxWallTime, projectCode, fileStagerPath
from src.stringUtilities import stripWhiteSpace,stripSlash,parseTimeString

#A collection of jobs that are compatible to be wrapran.
#It is the responsibility of the user to ensure that jobs have compatible walltimes, node requirements, modules etc.

class Campaign(Base):
    __tablename__ = 'campaigns'
    __name__ = 'campaign'

    id = Column(Integer, primary_key=True)
    name = Column('name',String,unique=True,nullable=False)
    jobs = relationship("Job", back_populates="campaign",cascade="all, delete-orphan")
    header = Column('header',String)
    footer = Column('footer',String)
    checkHeader = Column('checkHeader',String)
    checkFooter = Column('checkFooter',String)
    _wallTime = Column('wallTime',Interval)
    _checkWallTime = Column('checkWallTime',Interval)

    @orm.reconstructor
    def init_on_load(self):
        atexit.register(self.__killStager)

    #Public Methods
    def statusReport(self,Session):
        #Produce a report on the status of jobs in this campaign
        reportString = ""
        reportString += "Campaign "+self.name+", id "+str(self.id)+" \n"
        reportString += str(len(self.jobs))+" total jobs \n"
        reportString += self.__statusCount(Session,"Accepted")+" jobs accepted \n"
        reportString += self.__statusCount(Session,"Missing Input")+" jobs missing input \n"
        reportString += self.__statusCount(Session,"Staging Required")+" jobs required input to be staged \n"
        reportString += self.__statusCount(Session,"Staging")+" jobs prestaging input \n"
        reportString += self.__statusCount(Session,"Ready")+" jobs ready for submission \n"
        reportString += self.__statusCount(Session,"Submitted")+" jobs submitted \n"
        reportString += self.__statusCount(Session,"R")+" jobs running \n"
        reportString += self.__statusCount(Session,"C")+" jobs complete \n"
        reportString += self.__statusCount(Session,"Checking")+" jobs being checked \n"
        reportString += self.__statusCount(Session,"Checked")+" jobs checked \n"
        reportString += self.__statusCount(Session,"Successful")+" jobs successful \n"
        reportString += self.__statusCount(Session,"Failed")+" jobs failed \n"
        reportString += self.__statusCount(Session,"Requires Attention")+" jobs require attention \n"
        return reportString

    def unfinishedBusiness(self,Session):
        #Return true if there are still jobs to be run
        for unfinishedStatus in ['Accepted','Missing Input','Staging Required','Staging','Ready','Submitted','R','C','Checking','Checked','Failed']:
            if (not int(self.__statusCount(Session,unfinishedStatus)) == int(0)):
                return True
        return False

    def stageIn(self,Session):
        #Find out which jobs have files that require staging
        #Them launch the staging-in process
        #Return true if stager is launched or on-going
        #Return False if no stager is required

        #Find out what's going on with previous stager, if it exists
        #If it exists and is still running, don't launch another
        #If it exists and has finished, check to see that files were successfully staged, and launch another if necessary
        #If it doesn't exist, launch it

        #Do we have a currently running stager?
        if (self.__checkStager()):
            print "Existing Stager"
            return True

        #Which jobs have files that require staging?
        self.__checkInput(Session)

        #Create a list of all files that require staging
        stageInList = []
        for j in self.jobs:
            if (j.status == "Staging Required"):
                stageInList += j.listStageInFiles(Session)
                j.status = "Staging"
            #If we previously launched a stager that has now terminated, jobs still marked "Staging" have failed to stage in all files, so try again
            if (hasattr(self,'stagerProcess') and j.status == "Staging"):
                stageInList += j.listStageInFiles(Session)
                j.status = "Staging"
        Session.commit()
        #If nothing requires staging, we should return False
        if (stageInList == []):
            print "No Staging Required"
            return False
        print "Staging :"+str(stageInList)
        #Otherwise, launch a stager
        #Construct a bash script that runs the stager
        stagerScriptLoc = self.__createStagingScript(Session,stageInList)
        #run the script
        cmd = "bash "+stagerScriptLoc
        self.stagerProcess = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
        return True

    def submitJobs(self,Session,maxNodes=totalNodes,maxJobs=-1):
        #submit a bundle of up to maxJobs jobs that occupy fewer than maxNodes nodes
        #return number of nodes submitted
        if(maxJobs == -1):
            maxJobs = len(self.jobs)

        self.__checkInput(Session)
        #list of jobs to submit
        jobList = []
        jobCount = 0
        nodeCount = 0
        for j in self.jobs:
            if (j.status == "Ready" and j.nodes+nodeCount <= maxNodes):
                jobList.append(j)
                nodeCount += j.nodes
                jobCount += 1
            if (jobCount == maxJobs):
                break
        if (len(jobList) > 0):
            scriptName = self.__createSubmissionScript(Session,jobList)
            cmd = "qsub "+scriptName
            pbsSubmit = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
            pbsID = pbsSubmit.stdout.read().strip()
            try:
                int(pbsID)
            except ValueError:
                return 0
            else:
                for j in jobList:
                    j.pbsID = pbsID
                    j.status = "Submitted"
                Session.commit()
                return nodeCount
        else:
            return 0

    def submitCheckJobs(self,Session,maxNodes=totalNodes,maxJobs=-1):
        #submit a bundle of up to maxJobs job checks that occupy fewer than maxNodes nodes
        #return number of nodes submitted
        if (maxJobs == -1):
            maxJobs = len(self.jobs)

        #list of jobs to submit
        jobList = []
        jobCount = 0
        nodeCount = 0
        for j in self.jobs:
            if (j.status == "C" and j.checkNodes+nodeCount <= maxNodes and j.checkOutputCommand):
                jobList.append(j)
                nodeCount += j.checkNodes
                jobCount += 1
            if (jobCount == maxJobs):
                break
        if (len(jobList) > 0):
            scriptName = self.__createCheckSubmissionScript(Session,jobList)
            cmd = "qsub "+scriptName
            pbsSubmit = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
            pbsID = pbsSubmit.stdout.read().strip()
            try:
                int(pbsID)
            except ValueError:
                return 0
            else:
                for j in jobList:
                    j.checkPbsID = pbsID
                    j.status = "Checking"
                Session.commit()
                return nodeCount
        else:
            return 0

    def checkCompletionStatus(self,Session,jobList=[],currentlySubmittedJobsDict={}):
        if (jobList == []):
            jobList = self.jobs
        successList = []
        for j in jobList:
            #Check if completed happily
            if (j.status == 'Checked' or (j.status == 'C' and j.checkOutputScript is None)):
                if(j.checkCompletionStatus(Session)):
                    j.status = 'Successful'
                    successList.append(j)
                else:
                    print("Failed due to check failing")
                    j.status = 'Failed'
                    j.numFails += 1
            #If submitted or running and the pbs job has finished without reporting back, that's bad.
            elif (j.status in ['Submitted','R']):
                if (str(j.pbsID) in currentlySubmittedJobsDict):
                    if (currentlySubmittedJobsDict[str(j.pbsID)] in ['C','F','E']):
                        print("Failed due to submission completing without reporting")
                        j.status = 'Failed'
                        j.numFails += 1
                else:
                    print("Failed due to lost submission")
                    print("Expecting to find pbsID: "+str(j.pbsID))
                    j.status = 'Failed'
                    j.numFails += 1
            #Similarly for checking
            elif (j.status == 'Checking'):
                if (str(j.checkPbsID) in currentlySubmittedJobsDict):
                    if (currentlySubmittedJobsDict[str(j.checkPbsID)] in ['C','F','E']):
                        print("Failed due to check completing without reporting")
                        j.status = 'Failed'
                        j.numFails += 1
                else:
                    print("Failed due to lost check")
                    print("Expecting to find pbsID: "+str(j.checkPbsID))
                    j.status = 'Failed'
                    j.numFails += 1

        Session.commit()
        return successList

    #hybrid properties

    @hybrid_property
    def wallTime(self):
        if (self._wallTime):
            return self._wallTime
        else:
            maxWT = parseTimeString("00:00:10")
            for j in self.jobs:
                if ((j.wallTime is not None) and j.wallTime >maxWT):
                    maxWT = j.wallTime
            return maxWT

    @hybrid_property
    def checkWallTime(self):
        if (self._checkWallTime):
            return self._checkWallTime
        else:
            maxWT = parseTimeString("00:00:10")
            for j in self.jobs:
                if ((j.checkWallTime is not None) and j.checkWallTime >maxWT):
                    maxWT = j.checkWallTime
            return maxWT

    @wallTime.setter
    def wallTime(self,wallTime):
        self._wallTime = wallTime

    @checkWallTime.setter
    def checkWallTime(self,checkWallTime):
        self._checkWallTime = checkWallTime

    ## Private Methods

    def __checkStager(self):
        #Return true if this campaign has an active stager
        #False otherwise
        if (not hasattr(self,'stagerProcess')):
            return False
        else:
            rC = self.stagerProcess.poll()
            if (rC):
                return True
            else:
                return False

    def __createStagingScript(self,Session,stageInList):
        scriptName = self.name+"Stager.bash"
        with open(scriptName,'w') as script:
            script.write("source "+virtualEnvPath+"\n")
            updateString = "python "+fileStagerPath+" '"
            for f in stageInList:
                updateString += str(f.id)
            updateString += "' \n"
            script.write(updateString)
            script.write("deactivate\n")
        return scriptName

    def __createSubmissionScript(self, Session, jobList):
        #construct a job submission script from a list of jobs
        scriptName = self.name+".csh"
        nodes = 0
        wraprun = 'wraprun '
        for j in jobList:
            nodes += j.nodes
            wraprun += '-n '+str(j.nodes)
            wraprun += ' '+j.executionCommand+' : '
        wraprun = wraprun[:-2]
        with open(scriptName,'w') as script:
            script.write("#PBS -A "+projectCode+"\n")
            script.write("#PBS -N "+self.name+"\n")
            if(self.wallTime):
                script.write("#PBS -l walltime="+str(self.wallTime)+"\n")
            else: 
                maxWT = parseTimeString("00:00:10")
                for j in jobList:
                    if ((j.wallTime is not None) and j.wallTime > maxWT):
                        maxWT = j.wallTime
                script.write("#PBS -l walltime="+str(maxWT)+"\n")
            script.write("#PBS -l nodes="+str(nodes)+"\n")
            script.write("#PBS -j oe \n")

            script.write(self.header+"\n")

            script.write("source "+virtualEnvPath+"\n")
            updateString = "python "+jobStatusManagerPath+" updateJobStatus '"
            for j in jobList:
                updateString += str(j.id)+" "
            updateString += "' R\n"
            script.write(updateString)
            script.write("deactivate\n")
            script.write(wraprun+"\n")
            script.write(str(self.footer)+"\n")
            script.write("source "+virtualEnvPath+"\n")
            updateString = "python "+jobStatusManagerPath+" updateJobStatus '"
            for j in jobList:
                updateString += str(j.id)+" "
            updateString += "' C\n"
            script.write(updateString)
            script.write("deactivate\n")
        return scriptName

    def __createCheckSubmissionScript(self, Session, jobList):
        #construct a job check submission script from a list of jobs
        scriptName = self.name+"Check.csh"
        nodes = 0
        wraprun = 'wraprun '
        for j in jobList:
            if (j.checkOutputCommand):
                nodes += j.nodes
                wraprun += '-n '+str(j.nodes)
                wraprun += ' '+j.checkOutputCommand+' : '
            else:
                print "Warning: job " + j.jobName+", "+str(j.id)+" has no check script"
        wraprun = wraprun[:-2]
        with open(scriptName,'w') as script:
            script.write("#PBS -A "+projectCode+"\n")
            script.write("#PBS -N "+self.name+"Check\n")
            if(self.wallTime):
                script.write("#PBS -l walltime="+str(self.checkWallTime)+"\n")
            else: 
                maxWT = parseTimeString("00:00:10")
                for j in jobList:
                    if ((j.checkWallTime is not None) and j.checkWallTime > maxWT):
                        maxWT = j.checkWallTime
                script.write("#PBS -l walltime="+str(maxWT)+"\n")
            script.write("#PBS -l nodes="+str(nodes)+"\n")
            script.write("#PBS -j oe \n")

            script.write(self.checkHeader+"\n")
            script.write(wraprun+"\n")
            script.write(str(self.checkFooter)+"\n")
            script.write("source "+virtualEnvPath+"\n")
            updateString = "python "+jobStatusManagerPath+" updateJobStatus '"
            for j in jobList:
                updateString += str(j.id)+" "
            updateString += "' Checked\n"
            script.write(updateString)
            script.write("deactivate\n")
        return scriptName

    def __checkInput(self,Session,jobList=[]):
        if(jobList == []):
            jobList = self.jobs
        for j in jobList:
            if (j.status in ["Accepted", "Failed", "Missing Input", "Staging", "Staging Required"]):
                status = j.checkInput(Session)
                if (status in ["Staging Required", "Missing Input"]):
                    j.status = status
                elif (status == "Ready" and j.numFails < 5):
                    j.status =  "Ready"
                else:
                    j.status = "Requires Attention"
        Session.commit()

    def __statusCount(self,Session,status):
        #Return the number of jobs with status status in this campaign
        return str(Session.query(Job).filter(Job.campaignID == self.id).filter(Job.status == status).count())

    def __killStager(self):
        #Ensure a stager is killed if the main program exits
        if (self.__checkStager()):
            self.stagerProcess.kill()

    @staticmethod
    def _parseWallTime(mapper, connection, target):
        if (target._wallTime is not None):
            target._wallTime = parseTimeString(str(target._wallTime))
        if (target._checkWallTime is not None):
            target._checkWallTime = parseTimeString(str(target._checkWallTime))

    @staticmethod
    def _stripCampaignName(mapper, connection, target):
        if (target.name is not None):
            target.name = stripSlash(stripWhiteSpace(target.name))
#Event Listeners
#Process walltime and checkwalltime
listen(Campaign, 'before_insert', Campaign._parseWallTime)
listen(Campaign, 'before_update', Campaign._parseWallTime)
#Process name before inserting
listen(Campaign, 'before_insert', Campaign._stripCampaignName)
listen(Campaign, 'before_update', Campaign._stripCampaignName)
