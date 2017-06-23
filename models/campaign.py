import datetime, os, sys, subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, event, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, mapper, joinedload
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from src.base import Base
from job import Job
from env.environment import virtualEnvPath, jobStatusManagerPath, totalNodes
from src.stringUtilities import stripWhiteSpace,stripSlash

#A collection of jobs that are compatible to be wrapran.
#It is the responsibility of the user to ensure that jobs have compatible walltimes, node requirements, modules etc.
class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True)
    campaignName = Column('campaignName',String,unique=True)
    jobs = relationship("Job", back_populates="campaign")
    header = Column('header',String)
    footer = Column('footer',String)
    checkHeader = Column('checkHeader',String)
    checkFooter = Column('checkFooter',String)
    wallTime = Column('walltime',Interval)
    checkWallTime = Column('checkWallTime',Interval)

    #Public Methods
    def statusReport(self,Session):
        #Produce a report on the status of jobs in this campaign
        reportString = ""
        reportString += "Campaign "+self.campaignName+", id "+str(self.id)+" \n"
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
            if (not self.__statusCount(Session,int(unfinishedStatus)) == int(0)):
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
            if (j.status == "C" and j.checkNodes+nodeCount <= maxNodes and j.checkOutputScript):
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

    def checkCompletionStatus(self,Session,jobList=[]):
        if (jobList == []):
            jobList = self.jobs
        successList = []
        for j in jobList:
            if (j.status == 'Checked' or (j.status == 'C' and j.checkOutputScript is None)):
                if(j.checkCompletionStatus(Session)):
                    j.status = 'Successful'
                    successList.append(j)
                else:
                    j.status = 'Failed'
                    j.numFails += 1
        Session.commit()
        return successList

    ## Private Methods

    def __createSubmissionScript(self, Session, jobList):
        #construct a job submission script from a list of jobs
        scriptName = self.campaignName+".csh"
        nodes = 0
        wraprun = 'wraprun '
        for j in jobList:
            nodes += j.nodes
            wraprun += '-n '+str(j.nodes)
            wraprun += ' '+j.executionCommand+' : '
        wraprun = wraprun[:-2]
        print wraprun
        with open(scriptName,'w') as script:
            script.write("#PBS -A NPH103\n")
            script.write("#PBS -N "+self.campaignName+"\n")
            if(self.wallTime):
                script.write("#PBS -l walltime="+str(self.wallTime)+"\n")
            else: 
                script.write("#PBS -l walltime=01:00:00\n")
            script.write("#PBS -l nodes="+str(nodes)+"\n")
            script.write("#PBS -j oe \n")

            script.write(self.header+"\n")

            script.write("source "+virtualEnvPath+"\n")
            for j in jobList:
                script.write("python "+jobStatusManagerPath+" updateJobStatus "+str(j.id)+" R\n")
            script.write("deactivate\n")
            script.write(wraprun+"\n")
            script.write(str(self.footer)+"\n")
            script.write("source "+virtualEnvPath+"\n")
            for j in jobList:
                script.write("python "+jobStatusManagerPath+" updateJobStatus "+str(j.id)+" C\n")
            script.write("deactivate\n")
        return scriptName

    def __createCheckSubmissionScript(self, Session, jobList):
        #construct a job check submission script from a list of jobs
        scriptName = self.campaignName+"Check.csh"
        nodes = 0
        wraprun = 'wraprun '
        for j in jobList:
            if (j.checkOutputScript):
                nodes += j.nodes
                wraprun += '-n '+str(j.nodes)
                wraprun += ' '+j.checkOutputScript+' : '
            else:
                print "Warning: job " + j.jobName+", "+str(j.id)+" has no check script"
        wraprun = wraprun[:-2]
        print wraprun
        with open(scriptName,'w') as script:
            script.write("#PBS -A NPH103\n")
            script.write("#PBS -N "+self.campaignName+"Check\n")
            if(self.wallTime):
                script.write("#PBS -l walltime="+str(self.checkWallTime)+"\n")
            else: 
                script.write("#PBS -l walltime=01:00:00\n")
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
