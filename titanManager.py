import os, time, sys
from models.job import Job
from models.jobFile import File
from src.base import Base, session_scope, engine
from src.jobOps import submitJobs
from env import prodEnvironment
from src.stringUtilities import parseTimeString

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
    wT = parseTimeString(wallTime)
    eC = "echo 'test' >> "+os.path.join(outputDir,outputFiles[0])+"\n echo 'test' >> "+os.path.join(outputDir,outputFiles[1])
    testJob = Job(jobName="TestJob",executionCommand=eC,wallTime=wT)
    Session.add(testJob)
    Session.commit()
    testJobFile1 = File(fileName="output.txt",fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id,ioType='output')
    #testJobFile2 =  jobFile.File(fileName="otheroutput.txt",fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id,ioType='output')
    testJobFile2 = File(fileName="notes.txt",fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id,ioType='input')
    Session.commit()
    testJob.files = [testJobFile1,testJobFile2]
    print testJob.files
    print testJob.status
    submitJobs(False,False,Session)
    print testJob.status
    time.sleep(60)
    print testJob.pbsID,testJob.status

if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        main()
