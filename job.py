
#Job object:
    #Columns:
    #setup commands?
    #executable
    #aprun options
    #resources (nodes and time)
    #received date
    #status
    #run date (list?)
    #input
    #output
    #pbs id (list?)

    #methods:
    #create
    #getters/setters
    #check status
    #submit
    #cancel
    #check input/output files

from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON
import datetime
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from base import Base
import subprocess
from sqlalchemy import event
from sqlalchemy.orm import mapper
from sqlalchemy.inspection import inspect
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Job(Base):
    __tablename__ = 'jobs'
        
    id = Column(Integer, primary_key=True)
    jobName = Column('jobName',String)
    executionCommand = Column('executionCommand',String)
    nodes = Column('nodes',Integer)
    wallTime = Column('wallTime',Interval)
    status = Column('status',String)
    pbsID = Column('pbsID',Integer)
    files = relationship("File", back_populates="job")

    def submit(self,jobManagerPath,Session):
        ##Create script with appropriate information
        scriptName = self.jobName+".csh"
        with open(scriptName,'w') as script:
            script.write("#PBS -A NPH103\n")
            script.write("#PBS -N "+self.jobName+"\n")
            if(self.wallTime):
                script.write("#PBS -l walltime="+str(self.wallTime)+"\n")
            else: 
                script.write("#PBS -l walltime=01:00:00\n")
            if(self.nodes):
                script.write("#PBS -l nodes="+str(self.nodes)+"\n")
            else:
                script.write("#PBS -l nodes=1\n")

            script.write("#PBS -j oe \n")
            if ("virtualEnvPath" in os.environ) and ("envVarsPath" in os.environ):
                script.write("source "+os.environ["virtualEnvPath"]+"\n")
                script.write("python"+os.environ["envVarsPath"])
                script.write("python "+jobManagerPath+" updateJobStatus "+str(self.id)+" R\n")
            script.write("deactivate\n")
            script.write(self.executionCommand+"\n")
            if ("virtualEnvPath" in os.environ) and ("envVarsPath" in os.environ):
                script.write("source "+os.environ["virtualEnvPath"]+"\n")
                script.write("python "+jobManagerPath+" updateJobStatus "+str(self.id)+" C\n")
                script.write("python "+jobManagerPath+" checkJobStatus "+str(self.id)+"\n")
            script.write("deactivate\n")
        cmd = "qsub "+scriptName
        pbsSubmit = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
        self.pbsID = pbsSubmit.stdout.read().strip()
        self.status = "Submitted"
        Session.commit()

    def checkStatus(self,Session):
        status = self.status
        #If submitted but not yet run, do a qstat
        #Should avoid triggering this if at all possible
        if (status == 'Submitted'):
            cmd = "qstat -f "+str(self.pbsID)+" | grep 'job_state'"
            pbsCMD = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
            pbsStatus = pbsCMD.stdout.read()
            if (pbsStatus):
                status = str.split(pbsStatus)[2]
                self.status = status
            else:
                #if you have a pbs id but qstat is null, you've run
                if (os.path.exists(self.jobName+".o"+self.pbsID)):
                    status = "C"
                #this should never have to run
                else:
                    status = "Failed"
        #If your pbs status is C, check to see if the output files exist
        if(status == "C"):
            if(self.checkOutput):
                status = "Successful"
            else:
                status = "Failed"
        #commit changes
        self.status = status
        Session.commit()
        return status

    def checkOutput(self,Session):
        #Shouldn't do this unless pbs reports C
        if (not self.status == "C"):
            return "Incomplete"
        #check for output existence
        else:
            for oF in Session.query(Job,File).filter(Job.id == self.id).filter(File.jobID == self.id).filter(File.ioType == 'output').all():
                if (not oF.exists()):
                    return False
            return True

#EVENT LISTENERS

#Defaults
@event.listens_for(Job,"init")
def init(target, args, kwargs):
    target.status = "Accepted"
    if(not target.jobName):
        target.jobName = "Default"
    if(not target.executionCommand):
        target.executionCommand = "echo 'No Execution Command'"
    if(not target.nodes):
        target.nodes = 1
    if(not target.wallTime):
        target.wallTime = datetime.timedelta(hours=1)                
    target.pbsID = None
