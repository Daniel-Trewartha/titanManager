import os, sys, subprocess, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
import src.stringUtilities as stringUtilities
from env.currentAdaptor import adaptor as a

def getFreeResources():
	cmd = "squeue -a | grep ' R '"
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	freeNodes = int(a.totalNodes)
	minWallTime = datetime.timedelta(hours=3000)
	for line in str.split(qstatOut,'\n'):
		sLine = str.split(line)
		if (len(sLine) == 8):
			if(int(sLine[6])):
				freeNodes -= int(sLine[6])
			wallTime = stringUtilities.parseTimeString(str.split(line)[5])
			if (wallTime < minWallTime and wallTime.total_seconds() > 0):
				minWallTime = wallTime
	return freeNodes, minWallTime

def getQueuedJobs():
	cmd = "squeue -u "+a.user
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	queuedStats = ['Q','H','R','S']
	queuedJobs = 0
	for line in str.split(qstatOut,'\n'):
		splLine = str.split(line)
		if (len(splLine) == 8 and splLine[3] == a.user):
			if splLine[4] in queuedStats:
				queuedJobs += 1
	return queuedJobs

def getJobStatuses():
	cmd = "squeue -u "+a.user
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	jobsDict = {}
	for line in str.split(qstatOut,'\n'):
		splLine = str.split(line)
		if (len(splLine) == 8 and splLine[3] == a.user):
			jobsDict[splLine[0]] = splLine[4]
	return jobsDict
