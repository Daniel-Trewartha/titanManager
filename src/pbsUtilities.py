import os, sys, subprocess, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
import src.stringUtilities as stringUtilities
from env.environment import totalNodes,userName

def getFreeResources():
	cmd = "qstat -a | grep ' R '"
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	freeNodes = int(totalNodes)
	minWallTime = datetime.timedelta(hours=3000)
	for line in str.split(qstatOut,'\n'):
		sLine = str.split(line)
		if (len(sLine) == 11):
			if(int(sLine[5])):
				freeNodes -= int(sLine[5])
			wallTime = stringUtilities.parseTimeString(str.split(line)[8]) - stringUtilities.parseTimeString(str.split(line)[10])
			if (wallTime < minWallTime and wallTime.total_seconds() > 0):
				minWallTime = wallTime
	return freeNodes, minWallTime

def getQueuedJobs():
	cmd = "qstat -u "+userName
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	queuedStats = ['Q','H','R','S']
	queuedJobs = 0
	for line in str.split(qstatOut,'\n'):
		if (str.split(line)[1] == userName):
			if str.split(line)[9] in queuedStats:
				queuedJobs += 1
	return queuedJobs

def getJobStatuses():
	cmd = "qstat -u "+userName
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	jobsDict = {}
	for line in str.split(qstatOut,'\n'):
		splLine = str.split(line)
		if (splLine[1] == userName):
			jobsDict[splLine[0]] = splLine[9]
	return jobsDict