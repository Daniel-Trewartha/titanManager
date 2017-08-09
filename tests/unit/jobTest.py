import os,sys,inspect,re,subprocess,unittest 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'../..')))
import env.testEnvironment as testEnvironment
from faker import Faker
from tests.testUtils import dummyFile
from models.campaign import Campaign
from models.jobFile import File
from models.job import Job
from src.base import Base,session_scope,engine
from env.environment import cluster

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

	def test_flag_files_requiring_stage_in(self):
		with session_scope(engine) as Session:
			Session.add(self.dummyCampaign)
			Session.commit()
			testJob = Job(campaignID=self.dummyCampaign.id)
			Session.add(testJob)
			Session.commit()
			nonLocalFile = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input',cluster=self.fake.name())
			localFile = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input',cluster=cluster)
			Session.add(nonLocalFile)
			Session.commit()

			self.failUnless(testJob.checkInput(Session) == "Staging")

	def test_list_stage_in_files(self):
		with session_scope(engine) as Session:
			Session.add(self.dummyCampaign)
			Session.commit()
			testJob = Job(campaignID=self.dummyCampaign.id)
			Session.add(testJob)
			Session.commit()
			nonLocalFile = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input',cluster=self.fake.name())
			localFile = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input',cluster=cluster)
			Session.add(nonLocalFile)
			Session.commit()

			#We should get just nonLocalFile back
			self.failUnless(len(testJob.listStageInFiles(Session)) == 1)
			self.failUnless(testJob.listStageInFiles(Session)[0].id == nonLocalFile.id)

	def test_check_input_file_existence(self):
		with session_scope(engine) as Session:
			Session.add(self.dummyCampaign)
			Session.commit()
			testJob = Job(campaignID=self.dummyCampaign.id)
			Session.add(testJob)
			Session.commit()
			testFile1 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='output')
			testFile2 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input')
			testFile3 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input')
			Session.add(testFile1)
			Session.add(testFile2)
			Session.add(testFile3)
			Session.commit()

			#input files expected but do not exist
			self.failUnless(testJob.checkInput(Session) == "Missing Input")

			#input files expected but only some exist
			dummyFile(testFile2.filePath())
			self.failUnless(testJob.checkInput(Session) == "Missing Input")

			#input files expected, all exist, but output files do not
			dummyFile(testFile3.filePath())
			self.failUnless(testJob.checkInput(Session) == "Ready")
			os.remove(testFile2.filePath())
			os.remove(testFile3.filePath())

	def test_check_output_file_existence(self):
		with session_scope(engine) as Session:
			Session.add(self.dummyCampaign)
			Session.commit()
			testJob = Job(campaignID=self.dummyCampaign.id)
			Session.add(testJob)
			Session.commit()
			testFile1 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='output')
			testFile2 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='output')
			testFile3 = File(name=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id, ioType='input')
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


	def test_check_script_output(self):
		with session_scope(engine) as Session:
			Session.add(self.dummyCampaign)
			Session.commit()
			outputLoc = os.path.join(os.path.split(os.path.abspath(__file__))[0],self.fake.file_name())
			testJob = Job(campaignID=self.dummyCampaign.id,checkOutputScript="if [ -e "+outputLoc+" ]; then echo 'True'; fi")
			Session.add(testJob)
			Session.commit()

			self.failUnless(not testJob.checkCompletionStatus(Session))
			dummyFile(outputLoc)
			self.failUnless(testJob.checkCompletionStatus(Session))
			os.remove(outputLoc)

if __name__ == '__main__':
	unittest.main()
