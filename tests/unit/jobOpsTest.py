import os,sys,time,subprocess,unittest
sys.path.insert(0, os.path.abspath('../..'))
import env.testEnvironment as testEnvironment
from faker import Faker
from env.environment import virtualEnvPath
from models.jobFile import File
from models.job import Job
import src.jobOps as jobOps
from src.base import Base,session_scope,engine
from tests.testUtils import dummyFile

class jobTest(unittest.TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.fake = Faker()

	def tearDown(self):
		Base.metadata.drop_all(engine)

	#qdel a job
	def delJob(self,job):
		if (job.pbsID is not None):
			cmd = "qdel "+str(job.pbsID)
			qdel = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
			return True
		return False

	def test_update_job_status(self):
		with session_scope(engine) as Session:
			testJob = Job()
			Session.add(testJob)
			Session.commit()
			Session.refresh(testJob)
			cmd = "source "+virtualEnvPath+"\n"
			cmd += "python "+os.path.abspath(jobOps.__file__)+" updateJobStatus "+str(testJob.id)+" Teststatus\n"
			cmd += "deactivate\n"
			cmd += "exit"
		updateTest = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
		#make sure teardown doesn't drop all before updateTest runs
		#this is a massive hack - must make better
		time.sleep(5)
		self.failUnless(updateTest.stdout.read().strip().split()[-1] == "Teststatus")

	def test_check_job_status(self):
		with session_scope(engine) as Session:
			testJob = Job()
			testJob.status = "Teststatus"
			Session.add(testJob)
			Session.commit()
			Session.refresh(testJob)
			cmd = "source "+virtualEnvPath+"\n"
			cmd += "python "+os.path.abspath(jobOps.__file__)+" checkJobStatus "+str(testJob.id)+"\n"
			cmd += "deactivate\n"
			cmd += "exit"
		updateTest = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
		#make sure teardown doesn't drop all before updateTest runs
		#this is a massive hack - must make better
		time.sleep(5)
		self.failUnless(updateTest.stdout.read().strip().split()[-1] == "Teststatus")

	def test_job_submission(self):
		#To do: test walltime and node restriction
		with session_scope(engine) as Session:
			self.failUnless(jobOps.submitJobs(False,False,Session) == [])
			testJob = Job(jobName=self.fake.job(),nodes=1)
			Session.add(testJob)
			Session.commit()
			
			self.failUnless(jobOps.submitJobs(False,False,Session) == [testJob.id])
			self.failUnless(testJob.status == "Submitted")
			self.failUnless(testJob.pbsID is not None)

			self.failUnless(self.delJob(testJob))
			for f in os.listdir(os.path.split(os.path.abspath(__file__))[0]):
				if re.search(testJob.jobName+"\.*",f):
					os.remove(f)

	def test_failed_job_submission(self):
		#To do: test walltime and node restriction
		with session_scope(engine) as Session:
			self.failUnless(jobOps.rerunFailedJobs(False,False,Session) == [])
			testJob = Job(jobName=self.fake.job(),nodes=1)
			Session.add(testJob)
			testJob.status = 'Failed'
			Session.commit()
			
			self.failUnless(jobOps.rerunFailedJobs(False,False,Session) == [testJob.id])
			self.failUnless(testJob.status == "Submitted")
			self.failUnless(testJob.pbsID is not None)

			self.failUnless(self.delJob(testJob))
			for f in os.listdir(os.path.split(os.path.abspath(__file__))[0]):
				if re.search(testJob.jobName+"\.*",f):
					os.remove(f)


if __name__ == '__main__':
	unittest.main()
