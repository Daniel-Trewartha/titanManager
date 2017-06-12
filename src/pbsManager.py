import os, sys, subprocess, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
import src.stringUtilities as stringUtilities
from env.environment import totalNodes

def main():
	print "Commands for pbs"

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
