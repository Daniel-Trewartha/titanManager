#Separate out the executable functionality

import os, time, sys, datetime, subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from datetime import timedelta
from models.job import Job
from models.jobFile import File
import src.pbsManager as pbsManager
from src.base import Base,session_scope,engine
from src.stringUtilities import parseTimeString
from env.environment import virtualEnvPath,jobStatusManagerPath

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
    submitList = []
    eligibleJobs = filterEligibleJobs(isWallTimeRestricted, isNodeRestricted, "Ready", Session)
    for j in eligibleJobs:
        print "Submitting"
        print j.id, j.jobName
        submitList.append(j.id)
        j.submit(Session)
    return submitList

def rerunFailedJobs(isWallTimeRestricted, isNodeRestricted,Session):
    #Rerun Failed jobs, optionally only those that fit on current free resources
    eligibleJobs = filterEligibleJobs(isWallTimeRestricted, isNodeRestricted, "Failed", Session)
    submitList = []
    for j in eligibleJobs:
        print "Submitting"
        print j.id, j.jobName
        j.submit(Session)
        submitList.append(j.id)
    return submitList

def bundleJobs(isWallTimeRestricted, isNodeRestricted, Session):
    checkInputFiles(Session)
    eligibleJobs = filterEligibleJobs(isWallTimeRestricted, isNodeRestricted, "Ready", Session)
    smallestJob = eligibleJobs.order_by(Job.nodes).first()
    jobs = []
    totalNodes = 0
    maxWT = parseTimeString("00:00:00")
    eC = "wraprun"
    for j in eligibleJobs:
        if ((j.nodes - smallestJob.nodes) == 0 and (j.wallTime - smallestJob.wallTime) < parseTimeString("01:00:00")):
            totalNodes += j.nodes
            if (j.wallTime > maxWT):
                maxWT = j.wallTime
            jobs.append(j)
            eC = eC + " -n "+str(j.nodes)+" "+j.executionCommand+" :"
    eC = eC[:-1]
    print len(jobs),totalNodes,maxWT, eC
    scriptName = "bundleJob.csh"
    if(len(jobs) > 0):
        with open(scriptName,'w') as script:
            script.write("#PBS -A NPH103\n")
            script.write("#PBS -N bundleJob\n")
            script.write("#PBS -l walltime="+str(maxWT)+"\n")
            script.write("#PBS -l nodes="+str(totalNodes)+"\n")
            script.write("#PBS -j oe \n")
            script.write("Module load wraprun \n")
            script.write("source "+virtualEnvPath+"\n")
            for j in jobs:
                script.write("python "+jobStatusManagerPath+" updateJobStatus "+str(j.id)+" R\n")
            script.write("deactivate\n")
            script.write(eC+"\n")
            script.write("source "+virtualEnvPath+"\n")
            for j in jobs:
                script.write("python "+jobStatusManagerPath+" updateJobStatus "+str(j.id)+" C\n")
                script.write("python "+jobStatusManagerPath+" checkJobStatus "+str(j.id)+"\n")
            script.write("deactivate\n")
        cmd = "qsub "+scriptName
        pbsSubmit = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
        pbsID = pbsSubmit.stdout.read().strip()
        try:
            int(pbsID)
        except ValueError:
            return False
        else:
            for j in jobs:
                j.pbsID = pbsID
                j.status = "Submitted"
            Session.commit()
            return True

#Filter jobs by isWallTimeRestricted,isNodeRestricted,Status
def filterEligibleJobs(isWallTimeRestricted, isNodeRestricted, status,Session):
    if (isWallTimeRestricted or isNodeRestricted):
        nodes, minWallTime = pbsManager.getFreeResources()
    else:
        nodes, minWallTime = (0,0)
    print "Available Resources: ", nodes, minWallTime
    eligibleJobs = Session.query(Job).filter(Job.status == status)
    if(isNodeRestricted):
        eligibleJobs.filter(Job.nodes <= nodes)
    if (isWallTimeRestricted):
        eligibleJobs.filter(Job.wallTime < minWallTime)
    return eligibleJobs