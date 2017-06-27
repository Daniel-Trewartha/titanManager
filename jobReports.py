from src.base import Base,session_scope,engine
import time
import os
from models.campaign import Campaign
from models.job import Job
from models.jobFile import File
import sys

def main():
    print("Job Reporter")

def jobStatuses():
    print("Campaigns: ")
    for c in Session.query(Campaign).all():
        print c.id, c.name
    print("Jobs: ")
    for j in Session.query(Job).all():
        print j.id, j.name, j.status, j.campaign.name
    print("Files: ")
    for f in Session.query(File).all():
        print f.id, f.name, f.job.name, f.job.campaign.name


if __name__ == '__main__':
    with session_scope(engine) as Session:
        if(len(sys.argv)>1):
            if (sys.argv[1] == 'jobStatuses'):
                print jobStatuses()
        else:
            main()
