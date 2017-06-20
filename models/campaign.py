import datetime, os, sys, subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, event, ForeignKey
from sqlalchemy.orm import relationship, mapper, joinedload
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from src.base import Base
from env.environment import virtualEnvPath, jobStatusManagerPath, totalNodes
from src.stringUtilities import stripWhiteSpace,stripSlash

#A collection of jobs that are compatible to be wrapran.
#It is the responsibility of the user to ensure that jobs have compatible walltimes, node requirements, modules etc.
class Campaign(Base):
	__tablename__ = 'campaigns'

	id = Column(Integer, primary_key=True)
	campaignName = Column('campaignName',String)
	jobs = relationship("Job", back_populates="Campaign")
	header = Column('header',String)
	footer = Column('footer',String)
	checkHeader = Column('checkHeader',String)
	checkFooter = Column('checkFooter',String)
	wallTime = Column('walltime',Interval)
	checkWallTime = Column('checkWallTime',Interval)

    #Public Methods

    def submitJobs(Self,Session,maxNodes=totalNodes,maxJobs=self.jobs.count()):
        #submit a bundle of up to maxJobs jobs that occupy fewer than maxNodes nodes
        #return number of nodes submitted

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
            scriptName = self.__createSubmissionScript(jobList)
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

    def submitCheckJobs(Self,Session,maxNodes=totalNodes,maxJobs=self.jobs.count()):
        #submit a bundle of up to maxJobs job checks that occupy fewer than maxNodes nodes
        #return number of nodes submitted
        #list of jobs to submit
        jobList = []
        jobCount = 0
        nodeCount = 0
        for j in self.jobs:
            if (j.status == "C" and j.checkNodes+nodeCount <= maxNodes):
                jobList.append(j)
                nodeCount += j.checkNodes
                jobCount += 1
            if (jobCount == maxJobs):
                break
        if (len(jobList) > 0):
            scriptName = self.__createCheckSubmissionScript(jobList)
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

    def checkCompletionStatus(self,Session,jobList=self.jobs):
        for j in jobList:
            if (j.status == 'Checked' or (j.status == 'C' and self.outputCheckScript is None)):
                if(j.checkCompletionStatus(Session)):
                    j.status == 'Successful'
                else:
                    j.status == 'Failed'
        return True

    ## Private Methods

	def __createSubmissionScript(self, Session, jobList):
        #construct a job submission script from a list of jobs
        scriptName = self.campaignName+".csh"
        nodes = 0
        wraprun = 'wraprun '
        for j in jobList:
        	nodes += j.nodes
        	wraprun += '-n '+j.nodes
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
            script.write(self.footer+"\n")
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
        	if (j.outputCheckScript):
	        	nodes += j.nodes
    	    	wraprun += '-n '+j.nodes
        		wraprun += ' '+j.outputCheckScript+' : '
        	else:
        		print "Warning: job " + j.jobName+", "+j.id+" has no check script"
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
			script.write(self.checkFooter+"\n")
            script.write("source "+virtualEnvPath+"\n")
            for j in jobList:
                script.write("python "+jobStatusManagerPath+" updateJobStatus "+str(j.id)+" Checked\n")
            script.write("deactivate\n")
        cmd = "qsub "+scriptName
        pbsSubmit = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
        pbsID = pbsSubmit.stdout.read().strip()
        try:
            int(pbsID)
        except ValueError:
            return False
        else:
        	for j in jobList:
	            j.checkPbsID = pbsID
            	j.status = "Submitted"
            Session.commit()
            return True

    def __checkInput(self,Session,jobList=self.jobs):
        for j in jobList:
            if (j.status == "Accepted" or j.status == "Failed"):
                if (j.checkInput(Session)):
                    j.status =  "Ready"
                else:
                    j.status = "Missing Input"
        Session.commit()