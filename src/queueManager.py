import os, time, sys, datetime, subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from datetime import timedelta
from models.job import Job
from models.jobFile import File
from models.campaign import Campaign
from src.base import Base,session_scope,engine
from src.stringUtilities import parseTimeString
from env.currentAdaptor import adaptor as a


def submitJobs(Session,isWallTimeRestricted, isNodeRestricted):
    if(isWallTimeRestricted or isNodeRestricted):
        nodes, wallTime = a.getFreeResources()
    if (not isNodeRestricted):
        nodes = a.totalNodes
    if (not isWallTimeRestricted):
        wallTime = parseTimeString(a.maxWallTime)
    availableJobs = int(a.maxJobs) - a.getQueuedJobs()
    submittedNodes = nodes
    submittedJobs = availableJobs
    #Submit checks before new jobs
    for c in Session.query(Campaign).all():
        if (availableJobs <= 0):
            break
        if (c.checkWallTime <= parseTimeString(a.maxWallTime)):
            tN = c.submitCheckJobs(Session,maxNodes=nodes)
            if (tN > 0):
                nodes -= tN
                availableJobs -= 1
    for c in Session.query(Campaign).all():
        if (availableJobs <= 0):
            break
        if (c.wallTime <= parseTimeString(a.maxWallTime)):
            tN = c.submitJobs(Session,maxNodes=nodes)
            if (tN > 0):
                nodes -= tN
                availableJobs -= 1
    submittedNodes -= nodes
    submittedJobs -= availableJobs
    return submittedNodes,submittedJobs
