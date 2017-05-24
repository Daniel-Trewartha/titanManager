
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

class Job(Base):
    __tablename__ = 'jobs'
        
    id = Column(Integer, primary_key=True)
    jobName = Column(String)
    executionCommand = Column(String)
    nodes = Column(Integer)
    #wallTime = column(interval)
    #receivedTime = column(datetime)
    #status = column(string)
    #inputFiles = column(json)
    #outputFiles = column(json)
    #pbsID = column(json)


    def submit(self):
        ##Create script with appropriate information
        scriptName = self.jobname+".csh"
        with open(scriptName,'w') as submissionScript:
            submissionScript.write("Test")
        os.system("qsub "+scriptName)

    

    
