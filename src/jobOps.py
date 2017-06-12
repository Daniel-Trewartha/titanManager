#Separate out the executable functionality

import os, time, sys, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from datetime import timedelta
from models.job import Job
from models.jobFile import File
import src.pbsManager as pbsManager
from src.base import Base,session_scope,engine

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
        j.submit(Session)
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
        j.submit(Session)
        submitList.append(j.id)
    return submitList