import time
import os
import job
import jobFile
import sys
from datetime import timedelta
import pbsManager
from base import Base,Session,engine

def updateJobStatus(jobID,status):
    thisJob = Session.query(job.Job).filter(job.Job.id == jobID).one()
    thisJob.status = status
    Session.commit()
    return "Updated job id "+jobID+" to "+str(status)

def checkJobStatus(jobID):
    thisJob = Session.query(job.Job).filter(job.Job.id == jobID).one()
    thisJob.checkStatus()
    return "Job status "+str(thisJob.status)

def submitJobs(isWallTimeRestricted, isNodeRestricted):
    #Submit jobs, optionally only those that fit on current free resources
    nodes, minWallTime = pbsManager.getFreeResources()
    print "Available Resources: ", nodes, minWallTime
    eligibleJobs = Session.query(job.Job).filter(job.Job.status == "Accepted")
    if(isNodeRestricted):
        eligibleJobs.filter(job.Job.nodes <= nodes)
    if (isWallTimeRestricted):
        eligibleJobs.filter(job.Job.wallTime < minWallTime)
    for j in eligibleJobs:
        print "Submitting"
        print j.id, j.jobName
        j.submit(os.path.abspath(__file__))

def rerunFailedJobs(isWallTimeRestricted, isNodeRestricted):
    #Rerun Failed jobs, optionally only those that fit on current free resources
    nodes, minWallTime = pbsManager.getFreeResources()
    print "Available Resources: ", nodes, minWallTime
    eligibleJobs = Session.query(job.Job).filter(job.Job.status == "Failed")
    if(isNodeRestricted):
        eligibleJobs.filter(job.Job.nodes <= nodes)
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
        print("Job Operations")