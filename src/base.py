import os,sys
sys.path.append(os.path.abspath('../env'))
from contextlib import contextmanager
from sqlalchemy import create_engine,event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from environment import localDBFile

Base = declarative_base()
engine = create_engine('sqlite:///'+localDBFile,echo=False)

def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')

event.listen(engine, 'connect', _fk_pragma_on_connect)

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