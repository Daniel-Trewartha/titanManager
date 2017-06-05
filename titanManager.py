import time
import os
import job
import jobFile
import sys
from datetime import timedelta
from base import Base,localDBFile,session_scope
from sqlalchemy import create_engine
from jobOps import submitJobs
import utilities
import pbsManager
from sqlalchemy.orm import sessionmaker

def main():
    #xml input
    #Take job as argument??
    #should be executable or argument for executable?

    #Have queue(database reqd.?)
    #Check Titan queue
    #submit if necessary
    #nurse job to good health
    #check success: output file presence(non-0 size), pbs report
    outputDir = os.path.split(os.path.abspath(__file__))[0]
    outputFiles = ["output.txt","otheroutput.txt"]
    wallTime = "00:00:10"
    wT = utilities.parseTimeString(wallTime)
    eC = "echo 'test' >> "+os.path.join(outputDir,outputFiles[0])+"\n echo 'test' >> "+os.path.join(outputDir,outputFiles[1])
    testJob = job.Job(jobName="TestJob",executionCommand=eC,wallTime=wT)
    Session.add(testJob)
    Session.commit()
    testJobFile1 =  jobFile.File(fileName="output.txt",fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id,ioType='output')
    testJobFile2 =  jobFile.File(fileName="otheroutput.txt",fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id,ioType='output')
    testJobFile2 =  jobFile.File(fileName="notes.txt",fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id,ioType='input')
    Session.commit()
    testJob.files = [testJobFile1,testJobFile2]
    print testJob.files
    print testJob.status
    submitJobs(False,False,Session)
    print testJob.status
    time.sleep(60)
    print testJob.pbsID,testJob.status

if __name__ == '__main__':
    engine = create_engine('sqlite:///'+localDBFile,echo=False)
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        main()