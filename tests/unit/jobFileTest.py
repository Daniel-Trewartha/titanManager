import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'../..')))
import unittest
from faker import Faker
import env.testEnvironment as testEnvironment
from tests.testUtils import assertIntegrityError,dummyFile
from models.jobFile import File
from models.job import Job
from src.base import Base,session_scope,engine

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