from sqlalchemy import exc

def assertIntegrityError(test,Session):
	try:
		Session.commit()
	except exc.IntegrityError:
		Session.rollback()
		test.failUnless(True)
	else:
		test.fail("Did not see integrity error")