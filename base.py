from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
Base = declarative_base()
localDBFile = os.path.split(os.path.abspath(__file__))[0]+"/manager.db"
engine = create_engine('sqlite:///'+localDBFile,echo=False)
DBSession = sessionmaker(bind=engine)
Session = DBSession()
Base.metadata.create_all(engine)
virtualEnvPath = os.path.join(os.path.split(os.path.abspath(__file__))[0],"titanManager","bin","activate")
totalNodes = 18649