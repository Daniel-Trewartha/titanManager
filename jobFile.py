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
from sqlalchemy.event import listen
from sqlalchemy import exc
from utilities import stripString

class File(Base):
    __tablename__ = 'files'
        
    id = Column(Integer, primary_key=True)
    fileName = Column('fileName',String,nullable=False)
    fileDir = Column('fileDir',String,nullable=False)
    jobID = Column('jobID',Integer,ForeignKey("jobs.id"),nullable=False)
    ioType = Column('ioType',String,default="output")
    Job = relationship("Job", back_populates="files")

    def filePath(self):
        return os.path.join(self.fileDir,self.fileName)

    def exists(self,Session):
        if (os.path.exists(self.filePath())):
            return True
        else:
            return False

    def remove(self,Session):
        if self.exists(Session):
            os.remove(self.filePath())
            return True
        else:
            return False

    @staticmethod
    def _stripFileNameDir(mapper, connection, target):
        if (target.fileName is not None):
            target.fileName = stripString(target.fileName)
        if (target.fileDir is not None):
            target.fileDir = stripString(target.fileDir)
        

#Process filename and dir before inserting
listen(File, 'before_insert', File._stripFileNameDir)
listen(File, 'before_update', File._stripFileNameDir)
