from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON
import datetime
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from base import Base
from sqlalchemy import event
from sqlalchemy.orm import mapper
from sqlalchemy.inspection import inspect
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class File(Base):
    __tablename__ = 'files'
        
    id = Column(Integer, primary_key=True)
    fileName = Column('fileName',String,nullable=False)
    fileDir = Column('fileDir',String,nullable=False)
    jobID = Column('jobID',Integer,ForeignKey("jobs.id"),nullable=False)
    ioType = Column('ioType',String)
    job = relationship("Job", back_populates="files")


    def exists(self,Session):
        if (os.path.exists(os.path.join(self.fileDir,self.fileName))):
            return True
        else:
            return False
#EVENT LISTENERS

#Defaults
@event.listens_for(File,"init")
def init(target, args, kwargs):
    if(not target.ioType):
        target.ioType = 'output'
    if(not target.fileDir):
        target.fileDir = os.path.split(os.path.abspath(__file__))[0]
