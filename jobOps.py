import time
import os
import job
import jobFile
import sys
from datetime import timedelta
import pbsManager
from base import Base,session_scope,engine

def updateJobStatus(jobID,status,Session):
    thisJob = Session.query(job.Job).filter(job.Job.id == jobID).one()
    thisJob.status = status
    Session.commit()
    return "Updated job id "+jobID+" to "+str(status)

def checkJobStatus(jobID,Session):
    thisJob = Session.query(job.Job).filter(job.Job.id == jobID).one()
    thisJob.checkStatus(Session)
    return "Job status "+str(thisJob.status)

def checkInputFiles(Session):
    eligibleJobs = Session.query(job.Job).filter(job.Job.status == "Accepted")
    for j in eligibleJobs:
        inputPresent = True
        for dummy,iF in Session.query(job.Job,jobFile.File).filter(job.Job.id == j.id).filter(jobFile.File.jobID == j.id).filter(jobFile.File.ioType == 'input').all():
                if (not iF.exists(Session)):
                    inputPresent = False
        if (inputPresent):
            j.status = "Ready"
        else:
            j.status = "Missing Input"
    Session.commit()


def submitJobs(isWallTimeRestricted, isNodeRestricted,Session):
    #Submit jobs, optionally only those that fit on current free resources
    checkInputFiles(Session)
    nodes, minWallTime = pbsManager.getFreeResources()
    print "Available Resources: ", nodes, minWallTime
    eligibleJobs = Session.query(job.Job).filter(job.Job.status == "Ready")
    if(isNodeRestricted):
        eligibleJobs.filter(job.Job.nodes <= nodes)
    if (isWallTimeRestricted):
        eligibleJobs.filter(job.Job.wallTime < minWallTime)
    for j in eligibleJobs:
        print "Submitting"
        print j.id, j.jobName
        j.submit(os.path.abspath(__file__),Session)

def rerunFailedJobs(isWallTimeRestricted, isNodeRestricted,Session):
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
        j.submit(os.path.abspath(__file__),Session)

if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        if(len(sys.argv)>1):
            if (sys.argv[1] == 'updateJobStatus' and len(sys.argv) == 4):
                print updateJobStatus(sys.argv[2],sys.argv[3],Session)
            elif (sys.argv[1] == 'checkJobStatus' and len(sys.argv) == 3):
                print checkJobStatus(sys.argv[2],Session)
        else:
            print("Job Operations")