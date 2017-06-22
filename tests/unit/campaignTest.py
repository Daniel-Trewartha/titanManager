import os,sys,inspect,re,subprocess,unittest 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'../..')))
import env.testEnvironment as testEnvironment
from faker import Faker
from tests.testUtils import dummyFile
from models.jobFile import File
from models.job import Job
from models.campaign import Campaign
from src.base import Base,session_scope,engine
from src.stringUtilities import parseTimeString

class campaignTest(unittest.TestCase):
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

	def delCheckJob(self,job):
		if (job.checkPbsID is not None):
			cmd = "qdel "+str(job.checkPbsID)
			qdel = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
			return True
		return False

	def test_job_submission(self):
		with session_scope(engine) as Session:
			testCampaign = Campaign(campaignName='test',header='import wraprun',checkHeader='import wraprun',wallTime=parseTimeString('00:01:00'),checkWallTime=parseTimeString('00:01:00'))
			Session.add(testCampaign)
			Session.commit()
			testJob1 = Job(jobName=self.fake.job(),nodes=1,campaignID=testCampaign.id)
			testJob2 = Job(jobName=self.fake.job(),nodes=2,campaignID=testCampaign.id)
			testJob3 = Job(jobName=self.fake.job(),nodes=1,campaignID=testCampaign.id)
			testJob4 = Job(jobName=self.fake.job(),nodes=1,campaignID=testCampaign.id)
			Session.add(testJob1)
			Session.add(testJob2)
			Session.add(testJob3)
			Session.add(testJob4)
			Session.commit()
			
			#submit max nodes 2 - should wrap and submit testJob1 and testJob3
			self.failUnless(testCampaign.submitJobs(Session,maxNodes=2) == 2)
			self.failUnless(testJob1.status == "Submitted")
			self.failUnless(testJob3.status == "Submitted")
			self.failUnless(testJob1.pbsID is not None)
			self.failUnless(testJob3.pbsID is not None)
			self.failUnless(testJob1.pbsID == testJob3.pbsID)
			self.failUnless(delJob(testJob1))
			self.failUnless(delJob(testJob3))

			#submit max jobs 1 - should submit testJob 2
			self.failUnless(testCampaign.submitJobs(Session,maxJobs=1) == 2)
			self.failUnless(testJob2.status == "Submitted")
			self.failUnless(testJob2.pbsID is not None)
			self.failUnless(delJob(testJob2))

			#testJob 4 should never have been submitted, but should be ready
			self.failUnless(testJob4.status == "Ready")

			for f in os.listdir(os.path.split(os.path.abspath(__file__))[0]):
				if re.search(testCampaign.campaignName+"\.*",f):
					os.remove(f)

	def test_check_job_submission(self):
		with session_scope(engine) as Session:
			testCampaign = Campaign(campaignName='test',header='import wraprun',checkHeader='import wraprun',wallTime=parseTimeString('00:01:00'),checkWallTime=parseTimeString('00:01:00'))
			Session.add(testCampaign)
			Session.commit()
			testJob1 = Job(jobName=self.fake.job(),nodes=1,checkOutputScript='pwd',campaignID=testCampaign.id)
			testJob2 = Job(jobName=self.fake.job(),nodes=1,checkOutputScript='pwd',campaignID=testCampaign.id)
			testJob3 = Job(jobName=self.fake.job(),nodes=1,campaignID=testCampaign.id)
			Session.add(testJob1)
			Session.add(testJob2)
			Session.add(testJob3)
			Session.commit()
			
			testJob1.status = "C"
			testJob2.status = "Ready"
			testJob3.status = "C"
			Session.commit()

			#Should only submit testJob1 - 2 has not run, 3 has no check script
			self.failUnless(testCampaign.submitCheckJobs(Session) == 1)
			self.failUnless(testJob1.status == "Checking")
			self.failUnless(testJob2.status == "Ready")
			self.failUnless(testJob3.status == "C")
			self.failUnless(testJob1.checkPbsID is not None)
			self.failUnless(testJob2.checkPbsID is None)
			self.failUnless(testJob3.checkPbsID is None)
			self.failUnless(delJob(testJob1))

			for f in os.listdir(os.path.split(os.path.abspath(__file__))[0]):
				if re.search(testCampaign.campaignName+"\.*",f):
					os.remove(f)

	def test_check_completion_status(self):
		with session_scope(engine) as Session:
			testCampaign = Campaign(campaignName='test',header='import wraprun',checkHeader='import wraprun',wallTime=parseTimeString('00:01:00'),checkWallTime=parseTimeString('00:01:00'))
			Session.add(testCampaign)
			Session.commit()
			
			existingDummyFile = os.path.join(os.path.split(os.path.abspath(__file__))[0],self.fake.file_name())
			notExistingDummyFile = os.path.join(os.path.split(os.path.abspath(__file__))[0],self.fake.file_name())
			
			testJob1 = Job(jobName=self.fake.job(),nodes=1,checkOutputScript='pwd',checkOutputLoc=existingDummyFile,campaignID=testCampaign.id)
			testJob2 = Job(jobName=self.fake.job(),nodes=1,checkOutputScript='pwd',checkOutputLoc=notExistingDummyFile,campaignID=testCampaign.id)
			testJob3 = Job(jobName=self.fake.job(),nodes=1,campaignID=testCampaign.id)
			testJob4 = Job(jobName=self.fake.job(),nodes=1,campaignID=testCampaign.id)

			Session.add(testJob1)
			Session.add(testJob2)
			Session.add(testJob3)
			Session.add(testJob4)
			Session.commit()


			testFile1 = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob3.id, ioType='output')
			testFile2 = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob4.id, ioType='output')
			Session.add(testFile1)
			Session.add(testFile2)

			testJob1.status = "Checked"
			testJob2.status = "Checking"
			testJob3.status = "C"
			testJob4.status = "Submitted"
			Session.commit()

			#to be marked as 'failed', a job should be marked as run and checked, but either fail its check output script, or have non-existent output files
			#should be no successful jobs here, output should be empty list
			self.failUnless(testCampaign.checkCompletionStatus(Session) == [])
			self.failUnless(testJob1.status == 'Failed')
			self.failUnless(testJob2.status == 'Checking')
			self.failUnless(testJob3.status == 'Failed')
			self.failUnless(testJob4.status == 'Submitted')

			dummyFile(existingDummyFile)
			dummyFile(testFile1.filePath())

			testJob1.status = "Checked"
			testJob2.status = "Checked"
			testJob3.status = "C"
			testJob4.status = "C"
			Session.commit()
			#to be marked as 'successful' a job should have completed its checkout, if it has it, and all output files should exist, if it has them

			self.failUnless(testCampaign.checkCompletionStatus(Session) == [testJob1,testJob3])
			self.failUnless(testJob1.status == 'Successful')
			self.failUnless(testJob2.status == 'Failed')
			self.failUnless(testJob3.status == 'Successful')
			self.failUnless(testJob4.status == 'Failed')

			os.remove(existingDummyFile)
			os.remove(testFile1.filePath())

if __name__ == '__main__':
	unittest.main()
