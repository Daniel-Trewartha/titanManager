from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
localDBFile = os.path.split(os.path.abspath(__file__))[0]+"/manager.db"
localTestDBFile = os.path.split(os.path.abspath(__file__))[0]+"/test.db"
virtualEnvPath = os.path.join(os.path.split(os.path.abspath(__file__))[0],"titanManager","bin","activate")
totalNodes = 18649

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
