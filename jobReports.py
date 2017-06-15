from src.base import Base,session_scope,engine
import time
import os
from models.job import Job
from models.jobFile import File
import sys

def main():
	print("Job Reporter")

def jobStatuses():
	for j in Session.query(Job):
		print j.id, j.jobName, j.status
	for f in Session.query(File):
		print f.id, f.fileName, f.jobID


if __name__ == '__main__':
    with session_scope(engine) as Session:
        if(len(sys.argv)>1):
            if (sys.argv[1] == 'jobStatuses'):
            	print jobStatuses()
        else:
            main()
