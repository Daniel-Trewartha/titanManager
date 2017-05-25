from base import Base,Session,engine
import time
import os
import job
import sys

def main():
	print("Job Reporter")

def jobStatuses():
	for j in Session.query(job.Job):
		print j.id, j.jobName, j.status


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    if(len(sys.argv)>1):
        if (sys.argv[1] == 'jobStatuses'):
            print jobStatuses()
    else:
        main()