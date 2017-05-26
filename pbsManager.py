import os
import sys
import subprocess
from base import totalNodes, Base, engine
import DateTime

def main():
	print "Commands for pbs"

def getFreeResources():
	cmd = "qstat -a | grep ' R '"
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	freeNodes = totalNodes
	for line in str.split(qstatOut,'\n'):
		sLine = str.split(line)
		if (len(sLine) == 11):
			if(int(sLine[5])):
				freeNodes -= int(sLine[5])
			print str.split(line)[8],str.split(line)[10]
	print freeNodes

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    if(len(sys.argv)>1):
        if (sys.argv[1] == 'getFreeResources'):
            print getFreeResources()
    else:
        main()
