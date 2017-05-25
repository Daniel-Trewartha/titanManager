import time
import os
import job
import sys
from datetime import timedelta
from base import Base,Session,engine


def main():
    #xml input
    #Take job as argument??
    #should be executable or argument for executable?

    #Have queue(database reqd.?)
    #Check Titan queue
    #submit if necessary
    #nurse job to good health
    #check success: output file presence(non-0 size), pbs report
    outputDir = os.path.split(os.path.abspath(__file__))[0]
    outputFiles = "output.txt"
    wallTime = "00:00:10"
    hms = str.split(wallTime,":")
    wT = timedelta(hours = int(hms[0]), minutes = int(hms[1]), seconds = int(hms[2]))
    testJob = job.Job(jobName="TestJob",outputDir=outputDir,outputFiles=outputFiles,executionCommand="echo 'test' >> "+os.path.join(outputDir,outputFiles),wallTime=wT)
    Session.add(testJob)
    Session.commit()
    print testJob.id
    print testJob.jobName
    print testJob.pbsID
    print testJob.wallTime
    testJob.submit(os.path.abspath(__file__))
    time.sleep(10)
    print testJob.status
    time.sleep(60)
    print testJob.status
    print testJob.pbsID 
    Session.commit()

def updateJobStatus(jobID,status):
    thisJob = Session.query(job.Job).filter(job.Job.id == jobID).first()
    if (thisJob):
        thisJob.status = status
        Session.commit()
        return "Updated job id "+jobID+" to "+str(status)
    else:
        return "No Job Found"

def checkJobStatus(jobID):
    thisJob = Session.query(job.Job).filter(job.Job.id == jobID).first()
    if (thisJob):
        thisJob.checkStatus()
        return "Job status "+str(thisJob.status)
    else:
        return "No Job Found"

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    if(len(sys.argv)>1):
        if (sys.argv[1] == 'updateJobStatus' and len(sys.argv) == 4):
            print updateJobStatus(sys.argv[2],sys.argv[3])
        elif (sys.argv[1] == 'checkJobStatus' and len(sys.argv) == 3):
            print checkJobStatus(sys.argv[2])
    else:
        main()