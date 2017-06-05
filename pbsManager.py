import os
import sys
import subprocess
from base import totalNodes
import datetime
import utilities

def main():
	print "Commands for pbs"

def getFreeResources():
	cmd = "qstat -a | grep ' R '"
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	freeNodes = totalNodes
	minWallTime = datetime.timedelta(hours=3000)
	for line in str.split(qstatOut,'\n'):
		sLine = str.split(line)
		if (len(sLine) == 11):
			if(int(sLine[5])):
				freeNodes -= int(sLine[5])
			wallTime = utilities.parseTimeString(str.split(line)[8]) - utilities.parseTimeString(str.split(line)[10])
			if (wallTime < minWallTime and wallTime.total_seconds() > 0):
				minWallTime = wallTime
	return freeNodes, minWallTime
