#Remove dependency on jobFile - use files attribute instead
import datetime, os, sys, subprocess
sys.path.append(os.path.abspath('../src'))
sys.path.append(os.path.abspath('../env'))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, event, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapper, joinedload
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from base import Base
from environment import virtualEnvPath
from stringUtilities import stripWhiteSpace,stripSlash

class Job(Base):
    __tablename__ = 'jobs'
        
    id = Column(Integer, primary_key=True)
    jobName = Column('jobName',String,default='default')
    executionCommand = Column('executionCommand',String,default="echo 'No Execution Command'")
    nodes = Column('nodes',Integer,default=1)
    wallTime = Column('wallTime',Interval,default=datetime.timedelta(hours=1))
    status = Column('status',String)
    pbsID = Column('pbsID',Integer)
    files = relationship("File", back_populates="Job")

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
            script.write("source "+virtualEnvPath+"\n")
            script.write("python "+jobManagerPath+" updateJobStatus "+str(self.id)+" R\n")
            script.write("deactivate\n")
            script.write(self.executionCommand+"\n")
            script.write("source "+virtualEnvPath+"\n")
            script.write("python "+jobManagerPath+" updateJobStatus "+str(self.id)+" C\n")
            script.write("python "+jobManagerPath+" checkJobStatus "+str(self.id)+"\n")
            script.write("deactivate\n")
        cmd = "qsub "+scriptName
        pbsSubmit = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
        pbsID = pbsSubmit.stdout.read().strip()
        try:
            int(pbsID)
        except ValueError:
            return False
        else:
            self.pbsID = pbsID
            self.status = "Submitted"
            Session.commit()
            return True

    def checkStatus(self,Session):
        status = self.status
        #If submitted but not yet run, do a qstat
        #Should avoid triggering this if at all possible
        if (status == 'Submitted' and self.pbsID is not None):
            cmd = "qstat -f "+str(self.pbsID)+" | grep 'job_state'"
            pbsCMD = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
            pbsStatus = pbsCMD.stdout.read()
            if (not str.split(pbsStatus) == []):
                pbsStatus = str.split(pbsStatus)[2]
                status = str.split(pbsStatus)[2]
                self.status = status
            else:
                #if you have a pbs id but qstat is null, you've run
                if (os.path.exists(self.jobName+".o"+str(self.pbsID))):
                    status = "C"
                #you have a pbs id but no output - bad
                else:
                    status = "Failed"
        #If your pbs status is C, check to see if the output files exist
        if(status == "C"):
            if(self.checkOutput(Session)):
                status = "Successful"
            else:
                status = "Failed"
        #commit changes
        self.status = status
        Session.commit()
        return status

    def checkOutput(self,Session):
        #check for output file existence
        for oF in [oF for oF in self.files if oF.ioType == 'output']:
            if (not oF.exists(Session)):
                return False
        return True

    def checkInput(self,Session):
        #check for input file existence
        #Apparently in memory is the only way to do this
        for iF in [iF for iF in self.files if iF.ioType == 'input']:
            if (not iF.exists(Session)):
                return False
        return True

    @staticmethod
    def _stripJobName(mapper, connection, target):
        if (target.jobName is not None):
            target.jobName = stripSlash(stripWhiteSpace(target.jobName))
#EVENT LISTENERS

#Defaults
@event.listens_for(Job,"init")
def init(target, args, kwargs):
    target.status = "Accepted"
    target.pbsID = None

#Process jobname before inserting
listen(Job, 'before_insert', Job._stripJobName)
listen(Job, 'before_update', Job._stripJobName)
