from sqlalchemy.ext.declarative import declarative_base
import os
import sys
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
if "localDBFile" in os.environ:
	engine = create_engine('sqlite:///'+os.environ["localDBFile"],echo=False)
else:
	sys.exit("Environment Variables Not Defined")

@contextmanager
def session_scope(engine):
    """Provide a transactional scope around a series of operations."""
    DBSession = sessionmaker(bind=engine)
    Session = DBSession()
    try:
        yield Session
        Session.commit()
    except:
        Session.rollback()
        raise
    finally:
        Session.close()