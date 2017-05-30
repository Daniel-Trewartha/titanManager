import time
import os
import job
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
    outputFiles = "output.txt"
    wallTime = "00:00:10"
    wT = utilities.parseTimeString(wallTime)
    testJob = job.Job(jobName="TestJob",outputDir=outputDir,outputFiles=outputFiles,executionCommand="echo 'test' >> "+os.path.join(outputDir,outputFiles),wallTime=wT)
    Session.add(testJob)
    Session.commit()
    outputFiles = "output2.txt"
    wallTime = "01:00:00"
    wT = utilities.parseTimeString(wallTime)
    testJob2 = job.Job(jobName="TestJob2",outputDir=outputDir,outputFiles=outputFiles,executionCommand="echo 'test2' >> "+os.path.join(outputDir,outputFiles),wallTime=wT)
    Session.add(testJob2)
    Session.commit()
    outputFiles = "output3.txt"
    wallTime = "01:00:00"
    nodes = 500
    wT = utilities.parseTimeString(wallTime)
    testJob3 = job.Job(nodes=nodes,jobName="TestJob3",outputDir=outputDir,outputFiles=outputFiles,executionCommand="echo 'test3' >> "+os.path.join(outputDir,outputFiles),wallTime=wT)
    Session.add(testJob3)
    Session.commit()
    submitJobs(True,True)
    submitJobs(False,True)
    submitJobs(True,True)
    time.sleep(60)
    print testJob.pbsID,testJob.status
    print testJob2.pbsID,testJob2.status
    print testJob3.pbsID,testJob3.status

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    if(len(sys.argv)>1):
        if (sys.argv[1] == 'updateJobStatus' and len(sys.argv) == 4):
            print updateJobStatus(sys.argv[2],sys.argv[3])
        elif (sys.argv[1] == 'checkJobStatus' and len(sys.argv) == 3):
            print checkJobStatus(sys.argv[2])
    else:
        main()