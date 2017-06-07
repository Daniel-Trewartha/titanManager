from sqlalchemy import exc
import os
from faker import Faker

#Test for the presence of a database integrity error
def assertIntegrityError(test,Session):
	try:
		Session.commit()
	except exc.IntegrityError:
		Session.rollback()
		test.failUnless(True)
	else:
		test.fail("Did not see integrity error")

#create a dummy file at filePath
def dummyFile(filePath):
	with open(filePath,'w') as f:
		f.write(Faker().sentence())
	if (os.path.exists(filePath)):
		return True
	else:
		return False