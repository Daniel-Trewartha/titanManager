import os, time, sys, datetime
from datetime import timedelta
from models.job import Job
from models.jobFile import File
import src.pbsManager as pbsManager
from src.base import Base,session_scope,engine

#An externally callable job update routine
def updateJobStatus(jobID,status,Session):
    for j in Session.query(Job).all():
        print j.id
    thisJob = Session.query(Job).filter(Job.id == jobID).one()
    thisJob.status = status
    Session.commit()
    return "Updated job id "+jobID+" to "+str(status)

#Externally callable job status checker
def checkJobStatus(jobID,Session):
    thisJob = Session.query(Job).filter(Job.id == jobID).one()
    thisJob.checkStatus(Session)
    return "Job status "+str(thisJob.status)

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
