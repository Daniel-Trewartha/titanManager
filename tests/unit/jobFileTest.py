import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir) 
sys.path.insert(0,parentparentdir)
import testEnvironment
from jobFile import File
from job import Job
from base import Base,session_scope,engine
from sqlalchemy import exc
from testUtils import assertIntegrityError,dummyFile
from faker import Faker

class jobFileTest(unittest.TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.fake = Faker()

	def tearDown(self):
		Base.metadata.drop_all(engine)

	def insertTestJob(self,Session):
		testJob = Job()
		Session.add(testJob)
		Session.commit()
		return testJob

	def test_file_insertion(self):
		with session_scope(engine) as Session:
			testJob = self.insertTestJob(Session)
			testFile = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id)
			Session.add(testFile)
			Session.commit()
			
			q = Session.query(File).filter(File.jobID == testJob.id)
			self.failUnless(Session.query(q.exists()))

			self.failUnless(testJob.files[0].id == testFile.id)

	def test_file_insertion_without_loc(self):
		with session_scope(engine) as Session:
			testJob = self.insertTestJob(Session)
			testFile = File(jobID=testJob.id)
			Session.add(testFile)
			
			assertIntegrityError(self,Session)

	def test_file_insertion_with_invalid_job(self):
		with session_scope(engine) as Session:
			testJob = self.insertTestJob(Session)
			testFile = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id+1)
			Session.add(testFile)
			
			assertIntegrityError(self,Session)

	def test_file_existence(self):
		with session_scope(engine) as Session:
			testJob = self.insertTestJob(Session)
			testFile = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id)
			Session.add(testFile)
			Session.commit()

			self.failUnless(not testFile.exists(Session))
			self.failUnless(not testFile.remove(Session))

			dummyFile(testFile.filePath())
			self.failUnless(testFile.exists(Session))
			self.failUnless(testFile.remove(Session))
			self.failUnless(not testFile.exists(Session))

	def test_file_remove(self):
		with session_scope(engine) as Session:
			testJob = self.insertTestJob(Session)
			testFile = File(fileName=self.fake.file_name(),fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id)
			Session.add(testFile)
			Session.commit()

			dummyFile(testFile.filePath())
			self.failUnless(testFile.remove(Session))
			self.failUnless(not testFile.exists(Session))

if __name__ == '__main__':
    unittest.main()