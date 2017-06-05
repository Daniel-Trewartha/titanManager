import unittest
from jobFile import File
from job import Job

class jobFileTest(unittest.TestCase):
	def test_file_insertion(self):
		testJob = Job()
		testFile = File(fileName="notes.txt",fileDir=os.path.split(os.path.abspath(__file__))[0],jobID=testJob.id)
		