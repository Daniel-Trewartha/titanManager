#What should the main executable do?
#It should probably check all jobs in the database
#run the appropriate ones
#backfill mode should be an env variable
#check outputs and such
#then produce a report
import os, time, sys
from env.currentAdaptor import adaptor as a
from models.job import Job
from models.jobFile import File
from models.campaign import Campaign
from src.base import Base, session_scope, engine
from src.queueManager import submitJobs
from src.stringUtilities import parseTimeString

def main():

	unfinishedBusiness = True
	while unfinishedBusiness:
		print "Campaign Status Report"
		for c in Session.query(Campaign).all():
			print c.statusReport(Session)
		print "Submitting jobs"
		sN,sJ = submitJobs(Session,a.backfillMode,a.backfillMode)
		print "Submitted "+str(sJ)+" jobs occupying "+str(sN)+" nodes"
		jobsDict = a.getJobStatuses()
		print "Currently queued jobs: "
		print jobsDict
		for c in Session.query(Campaign).all():
			sList = c.checkCompletionStatus(Session,jobsDict=jobsDict)
			print "Campaign "+c.name+" reports "+str(len(sList))+" new successful completions"
			for j in sList:
				print str(j.id)+" "+j.name+" successfully completed"
		unfinishedBusiness = False
		for c in Session.query(Campaign).all():
			if (c.unfinishedBusiness(Session)):
				unfinishedBusiness = True
		time.sleep(60)
		if (not os.path.exists(a.localDBFile)):
			break

if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        main()
