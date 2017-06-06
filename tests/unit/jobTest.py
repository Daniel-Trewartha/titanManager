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
from faker import Faker

class jobTest(unittest.TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.fake = Faker()

	def tearDown(self):
		Base.metadata.drop_all(engine)

	def test_job_submission(self):
		with session_scope(engine) as Session:
			testJob = Job()
			Session.add(testJob)
			Session.commit()
			
			q = Session.query(File).filter(File.jobID == testJob.id)
			self.failUnless(Session.query(q.exists()))

			self.failUnless(testJob.files[0].id == testFile.id)

if __name__ == '__main__':
    unittest.main()