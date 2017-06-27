import os,sys,inspect,re,subprocess,unittest 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'../..')))
import env.testEnvironment as testEnvironment
from faker import Faker
from tests.testUtils import dummyFile
from models.campaign import Campaign
from models.jobFile import File
from models.job import Job
from src.base import Base,session_scope,engine

class jobTest(unittest.TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.fake = Faker()
		self.dummyCampaign = Campaign(name='TestCampaign')

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

	def test_check_input_output_file_existence(self):
		with session_scope(engine) as Session:
			Session.add(self.dummyCampaign)
			Session.commit()
			testJob = Job(campainID=self.dummyCampaign.id)
			Session.add(testJob)
			Session.commit()
			testFile1 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='output')
			testFile2 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='output')
			testFile3 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input')
			testFile4 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input')
			Session.add(testFile1)
			Session.add(testFile2)
			Session.add(testFile3)
			Session.add(testFile4)
			Session.commit()

			#output files expected but do not exist
			self.failUnless(not testJob.checkCompletionStatus(Session))

			#output files expected but only some exist
			dummyFile(testFile1.filePath())
			self.failUnless(not testJob.checkCompletionStatus(Session))

			#output files expected, all exist, but input files do not
			dummyFile(testFile2.filePath())
			self.failUnless(testJob.checkCompletionStatus(Session))
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


	def test_check_script_output(self):
		with session_scope(engine) as Session:
			Session.add(self.dummyCampaign)
			Session.commit()
			outputLoc = os.path.join(os.path.split(os.path.abspath(__file__))[0],self.fake.file_name())
			testJob = Job(campaignID=self.dummyCampaign.id,checkOutputLoc=outputLoc)
			Session.add(testJob)
			Session.commit()

			self.failUnless(not testJob.checkCompletionStatus(Session))
			dummyFile(outputLoc)
			self.failUnless(testJob.checkCompletionStatus(Session))
			os.remove(outputLoc)

if __name__ == '__main__':
	unittest.main()
