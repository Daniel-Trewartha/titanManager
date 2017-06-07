import unittest
import os,sys,inspect,re
import subprocess
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir) 
sys.path.insert(0,parentparentdir)
import testEnvironment
import jobOps
from jobFile import File
from job import Job
from base import Base,session_scope,engine
from faker import Faker
from testUtils import dummyFile
from environment import virtualEnvPath

class jobTest(unittest.TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.fake = Faker()

	def tearDown(self):
		Base.metadata.drop_all(engine)

	def test_update_job_status(self):
		with session_scope(engine) as Session:
			testJob = Job()
			Session.add(testJob)
			Session.commit()
			print testJob.id
			cmd = "source "+virtualEnvPath+"\n"
			cmd += "python "+os.path.abspath(jobOps.__file__)+" updateJobStatus "+str(testJob.id)+" Teststatus\n"
			cmd += "deactivate\n"
			cmd += "exit"
			updateTest = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
			self.failUnless(testJob.status == "Teststatus")


if __name__ == '__main__':
    unittest.main()
