import os, time, sys, datetime
from datetime import timedelta
from models.campaign import Campaign
from models.job import Job
from models.jobFile import File
from src.base import Base,session_scope,engine

#An externally callable job update routine
def updateJobStatus(jobIDList,status,Session):
    for jID in str.split(jobIDList):
        thisJob = Session.query(Job).get(int(jID))
        thisJob.status = status
    Session.commit()
    return jobIDList

#Externally callable job status checker
def checkJobStatus(jobID,Session):
    thisJob = Session.query(Job).get(int(jobID))
    complete = thisJob.checkCompletionStatus(Session)
    return "Job complete: "+str(complete)

if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        if(len(sys.argv)>1):
            if (sys.argv[1] == 'updateJobStatus' and len(sys.argv) == 4):
                print updateJobStatus(sys.argv[2],sys.argv[3],Session)
            elif (sys.argv[1] == 'checkJobStatus' and len(sys.argv) == 3):
                print checkJobStatus(sys.argv[2],Session)
        else:
            print("Job Operations")
