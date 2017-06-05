from base import Base,session_scope,engine
from sqlalchemy import create_engine
import time
import os
import job
import jobFile
import sys

def main():
	print("Job Reporter")

def jobStatuses():
	for j in Session.query(job.Job):
		print j.id, j.jobName, j.status


if __name__ == '__main__':
    with session_scope(engine) as Session:
        if(len(sys.argv)>1):
            if (sys.argv[1] == 'jobStatuses'):
            	print jobStatuses()
        else:
            main()
