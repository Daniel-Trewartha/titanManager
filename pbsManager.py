import os
import sys
import subprocess
from base import totalNodes

def main(self):
	print "Commands for pbs"
def getFreeResources(self):
	cmd = "qstat -a"
	qstatOut = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read()
	freeNodes = totalNodes
	for line in qstatOut:
		print line

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    if(len(sys.argv)>1):
        if (sys.argv[1] == 'getFreeResources'):
            print getFreeResources
    else:
        main()