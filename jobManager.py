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
from models.campaign import Campaign
from src.base import Base, session_scope, engine
from src.queueManager import submitJobs
from src.stringUtilities import parseTimeString

def main():

	print "Campaign Status Report"
	for c in Campaign:
		print c.statusReport(Session)
	print "Submitting jobs"
	sN,sJ = submitJobs(Session,backfillMode,backfillMode)
	print "Submitted "+str(sJ)+" jobs occupying "+str(sN)+" nodes"
	for c in Campaign:
		sList = c.checkCompletionStatus(Session)
		print "Campaign "+c.campaignName+" reports "+str(len(sList))+"new successful completions"
		for j in sList:
			print str(j.id)+" "+j.jobName+" successfully completed"

if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        main()
