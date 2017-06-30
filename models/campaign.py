import datetime, os, sys, subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, event, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, mapper, joinedload
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from sqlalchemy.ext.hybrid import hybrid_property
from src.base import Base
from job import Job
from env.environment import virtualEnvPath, jobStatusManagerPath, totalNodes, maxWallTime, projectCode
from src.stringUtilities import stripWhiteSpace,stripSlash,parseTimeString

#A collection of jobs that are compatible to be wrapran.
#It is the responsibility of the user to ensure that jobs have compatible walltimes, node requirements, modules etc.
class Campaign(Base):
    __tablename__ = 'campaigns'
    __name__ = 'campaign'

    id = Column(Integer, primary_key=True)
    name = Column('name',String,unique=True)
    jobs = relationship("Job", back_populates="campaign",cascade="all, delete-orphan")
    header = Column('header',String)
    footer = Column('footer',String)
    checkHeader = Column('checkHeader',String)
    checkFooter = Column('checkFooter',String)
    _wallTime = Column('wallTime',Interval)
    _checkWallTime = Column('checkWallTime',Interval)

    #Public Methods
    def statusReport(self,Session):
        #Produce a report on the status of jobs in this campaign
        reportString = ""
        reportString += "Campaign "+self.name+", id "+str(self.id)+" \n"
        reportString += str(len(self.jobs))+" total jobs \n"
        reportString += self.__statusCount(Session,"Accepted")+" jobs accepted \n"
        reportString += self.__statusCount(Session,"Missing Input")+" jobs missing input \n"
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
        for unfinishedStatus in ['Accepted','Missing Input','Ready','Submitted','R','C','Checking','Checked','Failed']:
            if (not int(self.__statusCount(Session,unfinishedStatus)) == int(0)):
                return True
        return False

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

    def checkCompletionStatus(self,Session,jobList=[],jobsDict={}):
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
                if (j.pbsID in jobsDict):
                    if (jobsDict[j.pbsID] in ['C','F','E']):
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
                if (j.checkPbsID in jobsDict):
                    if (jobsDict[j.checkPbsID] in ['C','F','E']):
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
            script.write("deactivate\n")
            script.write(wraprun+"\n")
            script.write(str(self.footer)+"\n")
            script.write("source "+virtualEnvPath+"\n")
            updateString = "python "+jobStatusManagerPath+" updateJobStatus '"
            for j in jobList:
                updateString += str(j.id)+" "
            updateString += "' R\n"
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
            for j in jobList:
                script.write("python "+jobStatusManagerPath+" updateJobStatus "+str(j.id)+" Checked\n")
            script.write("deactivate\n")
        return scriptName

    def __checkInput(self,Session,jobList=[]):
        if(jobList == []):
            jobList = self.jobs
        for j in jobList:
            if (j.status == "Accepted" or j.status == "Failed" or j.status == "Missing Input"):
                if (j.checkInput(Session)):
                    if (j.numFails < 5):
                        j.status =  "Ready"
                    else:
                        j.status = "Requires Attention"
                else:
                    j.status = "Missing Input"
        Session.commit()

    def __statusCount(self,Session,status):
        #Return the number of jobs with status status in this campaign
        return str(Session.query(Job).filter(Job.campaignID == self.id).filter(Job.status == status).count())

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
