#Separate out the executable functionality

import os, time, sys, datetime
sys.path.append(os.path.abspath('../models'))
from datetime import timedelta
from job import Job
from jobFile import File
import pbsManager
from base import Base,session_scope,engine

#An externally callable job update routine
def updateJobStatus(jobID,status,Session):
    for j in Session.query(Job).all():
        print j.id
    thisJob = Session.query(Job).filter(Job.id == jobID).one()
    thisJob.status = status
    Session.commit()
    return "Updated job id "+jobID+" to "+str(status)

#Externally callable job status checker
def checkJobStatus(jobID,Session):
    thisJob = Session.query(Job).filter(Job.id == jobID).one()
    thisJob.checkStatus(Session)
    return "Job status "+str(thisJob.status)

#Check whether input files are present for all jobs
def checkInputFiles(Session):
    eligibleJobs = Session.query(Job).filter(Job.status == "Accepted")
    for j in eligibleJobs:
        inputPresent = j.checkInput(Session)
        if (inputPresent):
            j.status = "Ready"
        else:
            j.status = "Missing Input"
    Session.commit()


def submitJobs(isWallTimeRestricted, isNodeRestricted,Session):
    #Submit jobs, optionally only those that fit on current free resources
    checkInputFiles(Session)
    nodes, minWallTime = pbsManager.getFreeResources()
    submitList = []
    print "Available Resources: ", nodes, minWallTime
    eligibleJobs = Session.query(Job).filter(Job.status == "Ready")
    if(isNodeRestricted):
        eligibleJobs.filter(Job.nodes <= nodes)
    if (isWallTimeRestricted):
        eligibleJobs.filter(Job.wallTime < minWallTime)
    for j in eligibleJobs:
        print "Submitting"
        print j.id, j.jobName
        submitList.append(j.id)
        j.submit(os.path.abspath(__file__),Session)
    return submitList

def rerunFailedJobs(isWallTimeRestricted, isNodeRestricted,Session):
    #Rerun Failed jobs, optionally only those that fit on current free resources
    nodes, minWallTime = pbsManager.getFreeResources()
    print "Available Resources: ", nodes, minWallTime
    eligibleJobs = Session.query(Job).filter(Job.status == "Failed")
    submitList = []
    if(isNodeRestricted):
        eligibleJobs.filter(Job.nodes <= nodes)
    if (isWallTimeRestricted):
        eligibleJobs.filter(Job.wallTime < minWallTime)
    for j in eligibleJobs:
        print "Submitting"
        print j.id, j.jobName
        j.submit(os.path.abspath(__file__),Session)
        submitList.append(j.id)
    return submitList

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
