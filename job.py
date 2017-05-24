
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



class Job(Base):
    __tablename__ = 'jobs'
        
    id = Column(Integer, primary_key=True)
    jobName = Column('jobName',String)
    executionCommand = Column('executionCommand',String)
    nodes = Column('nodes',Integer)
    wallTime = Column('wallTime',Interval)
    #receivedTime = column(datetime)
    status = Column('status',String)
    #inputFiles = column(json)
    #outputFiles = column(json)
    pbsID = Column('pbsID',Integer)

    def submit(self):
        ##Create script with appropriate information
        scriptName = self.jobName+".csh"
        with open(scriptName,'w') as script:
            script.write("#PBS -A NPH103\n")
            script.write("#PBS -N "+self.jobName+"\n")
            #FORMAT THIS PROPERLY HH:MM:SS
            if(self.wallTime):
                script.write("#PBS -l walltime="+self.wallTime+"\n")
            else: 
                script.write("#PBS -l walltime=01:00:00\n")
            if(self.nodes):
                script.write("#PBS -l nodes="+self.nodes+"\n")
            else:
                script.write("#PBS -l nodes=1\n")
            script.write("#PBS -j oe \n")
            script.write(self.executionCommand)
        cmd = "qsub "+scriptName
        pbsSubmit = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
        self.pbsID = pbsSubmit.stdout.read().strip()

    def checkStatus(self):
        if (self.pbsID):
            cmd = "qstat -f "+str(self.pbsID)+" | grep 'job_state'"
            print(str(self.pbsID))
            print(cmd)
            pbsCMD = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
            pbsStatus = pbsCMD.stdout.read()
            #pbsStatus = 'job_state = C'
            if (pbsStatus):
                status = str.split(pbsStatus)[2]
                self.status = status
            else:
                status = "C"
        else:
            status = self.status        
        return status

#EVENT LISTENERS

#Defaults
@event.listens_for(Job,"init")
def init(target, args, kwargs):
    target.status = "Accepted"
    if(not target.jobName):
        target.jobName = "Default"
    if(not target.executionCommand):
        target.executionCommand = "echo 'No Execution Command'"
