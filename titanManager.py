import time
import os
import job
import sys
from datetime import timedelta
from base import Base,Session,engine
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
    submitRunnableJobs(True)
    submitRunnableJobs(False)
    time.sleep(60)
    print testJob.pbsID,testJob.status
    print testJob2.pbsID,testJob2.status
    print testJob3.pbsID,testJob3.status

def updateJobStatus(jobID,status):
    thisJob = Session.query(job.Job).filter(job.Job.id == jobID).first()
    if (thisJob):
        thisJob.status = status
        Session.commit()
        return "Updated job id "+jobID+" to "+str(status)
    else:
        return "No Job Found"

def checkJobStatus(jobID):
    thisJob = Session.query(job.Job).filter(job.Job.id == jobID).first()
    if (thisJob):
        thisJob.checkStatus()
        return "Job status "+str(thisJob.status)
    else:
        return "No Job Found"

def submitRunnableJobs(isWallTimeRestricted):
    #Submit jobs smaller than number of available nodes, optionally also within walltime limits
    nodes, minWallTime = pbsManager.getFreeResources()
    eligibleJobs = Session.query(job.Job).filter(job.Job.nodes <= nodes).filter(job.Job.status = "Accepted")
    if (isWallTimeRestricted):
        eligibleJobs.filter(job.Job.wallTime < minWallTime)
    for j in eligibleJobs:
        print "Submitting"
        print j.id, j.jobName
        j.submit(os.path.abspath(__file__))

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    if(len(sys.argv)>1):
        if (sys.argv[1] == 'updateJobStatus' and len(sys.argv) == 4):
            print updateJobStatus(sys.argv[2],sys.argv[3])
        elif (sys.argv[1] == 'checkJobStatus' and len(sys.argv) == 3):
            print checkJobStatus(sys.argv[2])
    else:
        main()