#What should the main executable do?
#It should probably check all jobs in the database
#run the appropriate ones
#backfill mode should be an env variable
#check outputs and such
#then produce a report
import os, time, sys
from env import prodEnvironment
from env.environment import backfillMode, cluster, localKeyFile
from models.job import Job
from models.jobFile import File
from models.campaign import Campaign
from src.base import Base, session_scope, engine
from src.campaignManager import submitJobs
from src.pbsUtilities import getJobStatuses
from src.stringUtilities import parseTimeString
from src.globusUtilities import testActivation

def main():

	if (backfillMode == "False"):
		bfM = False
	else:
		bfM = True
	#Acquire globus tokens, if we don't already have them
	testActivation(cluster,localKeyFile)
	unfinishedBusiness = True
	while unfinishedBusiness:
		print "Campaign Status Report"
		for c in Session.query(Campaign).all():
			print c.statusReport(Session)
		print "Checking for required staging"
		for c in Session.query(Campaign).all():
			c.stageIn(Session)
		print "Submitting jobs"
		sN,sJ = submitJobs(Session,bfM,bfM)
		print "Submitted "+str(sJ)+" jobs occupying "+str(sN)+" nodes"
		jobsDict = getJobStatuses()
		print "Currently queued jobs: "
		print jobsDict
		for c in Session.query(Campaign).all():
			sList = c.checkCompletionStatus(Session,currentlySubmittedJobsDict=jobsDict)
			print "Campaign "+c.name+" reports "+str(len(sList))+" new successful completions"
			for j in sList:
				print str(j.id)+" "+j.name+" successfully completed"
		unfinishedBusiness = False
		for c in Session.query(Campaign).all():
			if (c.unfinishedBusiness(Session)):
				unfinishedBusiness = True
			else:
				c.cleanUp(Session)
		time.sleep(5)

if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        main()
