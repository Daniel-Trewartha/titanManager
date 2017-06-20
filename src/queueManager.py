import os, time, sys, datetime, subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from datetime import timedelta
from models.job import Job
from models.jobFile import File
from models.campaign import Campaign
import src.pbsUtilities as pbsUtilities
from src.base import Base,session_scope,engine
from src.stringUtilities import parseTimeString
from env.environment import virtualEnvPath,jobStatusManagerPath,totalNodes,maxWallTime,maxJobs


def submitJobs(Session,isWallTimeRestricted, isNodeRestricted):
    if(isWallTimeRestricted or isNodeRestricted):
        nodes, wallTime = pbsUtilities.getFreeResources()
    if (not isNodeRestricted):
        nodes = totalNodes
    if (not isWallTimeRestricted):
        wallTime = maxWallTime
    availableJobs = int(maxJobs) - pbsUtilities.getQueuedJobs()
    submittedNodes = nodes
    submittedJobs = availableJobs
    #Submit checks before new jobs
    for c in Session.query(Campaign).all():
        if (availableJobs <= 0):
            break
        if (c.checkWallTime <= maxWallTime):
            nodes -= c.submitCheckJobs(Session,maxNodes=nodes)
            availableJobs -= 1
    for c in Session.query(Campaign).all():
        if (availableJobs <= 0):
            break
        if (c.wallTime <= maxWallTime):
            nodes -= c.submitJobs(Session,maxNodes=nodes)
            availableJobs -= 1
    submittedNodes -= nodes
    submittedJobs -= availableJobs
    return submittedNodes,submittedJobs