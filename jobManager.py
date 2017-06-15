#What should the main executable do?
#It should probably check all jobs in the database
#run the appropriate ones
#backfill mode should be an env variable
#check outputs and such
#then produce a report
import os, time, sys
from env import prodEnvironment
from env.environment import backfillMode
from models.job import Job
from models.jobFile import File
from src.base import Base, session_scope, engine
from src.jobOps import submitJobs, rerunFailedJobs, bundleJobs, checkJobsStatus, checkInputFiles
from src.stringUtilities import parseTimeString

def main():

	completeJobs = Session.query(Job).filter(Job.status == "C").count()
	failedJobs = Session.query(Job).filter(Job.status == "Failed").count()
	successfulJobs = Session.query(Job).filter(Job.status == "Successful").count()
	print(str(completeJobs) + " jobs have finished running")
	print("Checking job status")
	checkJobsStatus(Session)
	print(str(Session.query(Job).filter(Job.status == "Successful").count() - successfulJobs) + " jobs successfully ran")
	print(str(Session.query(Job).filter(Job.status == "Failed").count() - failedJobs) + " jobs failed")
	checkInputFiles(Session)
	readyJobs = Session.query(Job).filter(Job.status == "Ready")
	missingInputJobs = Session.query(Job).filter(Job.status == "Missing Input")
	print(str(missingInputJobs.count()) + " jobs missing input files")
	for j in missingInputJobs.all():
		print ("Job id: "+str(j.id)+", jobName: "+j.jobName+" missing input files")
	print(str(readyJobs.count()) + " jobs ready for submission")
	print("Submitting ready jobs")
	print("Backfill Mode : " + str(backfillMode))
	submittedJobs = submitJobs(backfillMode,backfillMode,Session)
	for j in submittedJobs:
		print ("Job id: "+str(j.id)+", jobName: "+j.jobName+" submitted")
	print("Rerunning failed jobs")
	rerunJobs = rerunFailedJobs(backfillMode,backfillMode,Session)
	for j in rerunJobs:
		print ("Job id: "+str(j.id)+", jobName: "+j.jobName+" submitted")	


if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        main()
