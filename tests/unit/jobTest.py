import os,sys,inspect,re,subprocess,unittest 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'../..')))
import env.testEnvironment as testEnvironment
from faker import Faker
from tests.testUtils import dummyFile
from models.jobFile import File
from models.job import Job
from src.base import Base,session_scope,engine

class jobTest(unittest.TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.fake = Faker()

	def tearDown(self):
		Base.metadata.drop_all(engine)
		#Clean up job submission scripts from failed tests
		for f in os.listdir(os.path.split(os.path.abspath(__file__))[0]):
			if re.search('\S*csh',f):
				os.remove(f)		

	#qdel a job
	def delJob(self,job):
		if (job.pbsID is not None):
			cmd = "qdel "+str(job.pbsID)
			qdel = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
			return True
		return False

	def test_job_submission(self):
		with session_scope(engine) as Session:
			testJob = Job(jobName=self.fake.job())
			Session.add(testJob)
			Session.commit()
			
			#submit a fake path for job manager path - we are not testing the job manager here
			self.failUnless(testJob.submit(self.fake.file_path(depth=3),Session))
			self.failUnless(testJob.status == "Submitted")
			self.failUnless(testJob.pbsID is not None)

			self.failUnless(self.delJob(testJob))
			for f in os.listdir(os.path.split(os.path.abspath(__file__))[0]):
				if re.search(testJob.jobName+"\.*",f):
					os.remove(f)

	def test_check_input_output(self):
		with session_scope(engine) as Session:
			testJob = Job()
			Session.add(testJob)
			Session.commit()
			testFile1 = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='output')
			testFile2 = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='output')
			testFile3 = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input')
			testFile4 = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input')
			Session.add(testFile1)
			Session.add(testFile2)
			Session.add(testFile3)
			Session.add(testFile4)
			Session.commit()

			#output files expected but do not exist
			self.failUnless(not testJob.checkOutput(Session))

			#output files expected but only some exist
			dummyFile(testFile1.filePath())
			self.failUnless(not testJob.checkOutput(Session))

			#output files expected, all exist, but input files do not
			dummyFile(testFile2.filePath())
			self.failUnless(testJob.checkOutput(Session))
			os.remove(testFile1.filePath())
			os.remove(testFile2.filePath())

			#input files expected but do not exist
			self.failUnless(not testJob.checkInput(Session))

			#input files expected but only some exist
			dummyFile(testFile3.filePath())
			self.failUnless(not testJob.checkInput(Session))

			#input files expected, all exist, but output files do not
			dummyFile(testFile4.filePath())
			self.failUnless(testJob.checkInput(Session))
			os.remove(testFile3.filePath())
			os.remove(testFile4.filePath())

	def test_check_status(self):
		with session_scope(engine) as Session:
			testJob = Job()
			testJob.status = 'Submitted'
			#Dummy pbsID  - test real PBS IDs in integration tests
			testJob.pbsID = 1
			Session.add(testJob)
			Session.commit()

			#Status is submitted, no pbs output, no qstat result - should fail
			self.failUnless(testJob.checkStatus(Session) == 'Failed')

			#Status is submitted, pbs output exists, no output files expected - should be successful
			testJob.status = 'Submitted'
			Session.commit()
			dummyFile(testJob.jobName+".o"+str(testJob.pbsID))
			self.failUnless(testJob.checkStatus(Session) == "Successful")
			os.remove(testJob.jobName+".o"+str(testJob.pbsID))

			#Status is C, pbs output exists, output files expected but do not exist - should be failed
			testFile = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='output')
			Session.add(testFile)
			testJob.status = 'C'
			Session.commit()
			self.failUnless(testJob.checkStatus(Session) == "Failed")

			#Status is C, pbs output exists, output files expected and exist - should be successful
			testJob.status = 'C'
			dummyFile(testFile.filePath())
			Session.commit()
			self.failUnless(testJob.checkStatus(Session) == "Successful")
			os.remove(testFile.filePath())

if __name__ == '__main__':
	unittest.main()
