import abc, os
import ConfigParser

#An abstract class that defines information required to run on a cluster	

class systemAdaptor(object):
	__metaclass__ = abc.ABCMeta

	#A string command to enable the virtual env setup by setup
	@abc.abstractproperty
	def activateVirtualEnv(self):
		return

	#A string command to disable the virtual env setup by setup
	@abc.abstractproperty
	def deactivateVirtualEnv(self):
		return	

	#the location the sqlite database should be stored
	@abc.abstractproperty
	def localDBFile(self):
		return	

	#the location the job status manager executable is stored
	@abc.abstractproperty
	def jobStatusManagerPath(self):
		return	

	#The user who will be running on this cluster
	@abc.abstractproperty
	def user(self):
		return

	#A directory the example campaign can work out of
	@abc.abstractproperty
	def exampleWorkDir(self):
		return

	#The total nodes on this cluster
	@abc.abstractproperty
	def totalNodes(self):
		return

	#Provide a concrete implementation for pulling properties from config file
	#adaptor implementations can use these or not as they wish

	#Returns the config file object
	def config(self):
		config = ConfigParser.ConfigParser()
		configFile = os.path.join(os.path.split(os.path.abspath(__file__))[0],'config.ini')
		config.read(configFile)
		return config

	#The maximum time any job should be able to run
	@abc.abstractproperty
	def maxWallTime(self):
		return self.config().get("settings","maxwalltime")

	#The maximum number of batch jobs at any given time
	@abc.abstractproperty
	def maxJobs(self):
		return self.config().get("settings","maxjobs")

	#The number of times a job should be submitted before being marked as failed
	@abc.abstractproperty
	def maxJobFails(self):
		return self.config().get("settings","maxjobfails")

	#The number of times a job should be submitted before being marked as failed
	@abc.abstractproperty
	def backfillMode(self):
                if (self.config().get("settings","backfillmode") in ["True","true","T","t"]):
                        return True
                else:
                        return False

	#Receive a list of job objects from campaign in joblist
	#Construct a queue submission script
	#nodesAttr, wtAttr, execAttr are the job properties that give required nodes, wall time, execution command
	#startStat and endStat are the statuses job is updated to when script starts and finishes respectively
	#file suffix is appended to submission script names
	@abc.abstractmethod
	def createSubmissionScript(self, Session, campaign, jobList, nodesAttr, wtAttr, execAttr, startStat, endStat, fileSuffix):
		return

	#Install required packages, set up a virtualenv
	def setup(self):
		return

	#Get free nodes, minimum walltime on running jobs
	def getFreeResources(self):
		return

	#Return a list of all jobs in queue owned by user
	def getQueuedJobs(self):
		return

	#Return a dict of jobs owned by user with their status
	def getJobStatuses(self):
		return
