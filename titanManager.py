import time
import os
import job
import jobFile
import sys
from datetime import timedelta
from base import Base,Session,engine
from jobOps import submitJobs
import utilities
import pbsManager

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
    Session.commit()
    testJob.files = [testJobFile1,testJobFile2]
    print testJob.files
    submitJobs(True,True)
    submitJobs(False,True)
    submitJobs(True,True)
    time.sleep(60)
    print testJob.pbsID,testJob.status

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    if(len(sys.argv)>1):
        if (sys.argv[1] == 'updateJobStatus' and len(sys.argv) == 4):
            print jobOps.updateJobStatus(sys.argv[2],sys.argv[3])
        elif (sys.argv[1] == 'checkJobStatus' and len(sys.argv) == 3):
            print jobOps.checkJobStatus(sys.argv[2])
    else:
        main()