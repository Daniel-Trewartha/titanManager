import time
import os
import job
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