from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON
import datetime
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from base import Base,Session,virtualEnvPath
from sqlalchemy import event
from sqlalchemy.orm import mapper
from sqlalchemy.inspection import inspect
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class File(Base):
    __tablename__ = 'files'
        
    id = Column(Integer, primary_key=True)
    fileName = Column('fileName',String)
    fileDir = Column('fileDir',String)
    jobID = Column('jobID',Integer,ForeignKey("jobs.id"),nullable=False)

    job = relationship("Job", back_populates="files")


#EVENT LISTENERS

#Defaults
@event.listens_for(File,"init")
def init(target, args, kwargs):
    pass
