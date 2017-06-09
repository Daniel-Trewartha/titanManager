import datetime, os, sys
sys.path.append(os.path.abspath('../src'))
sys.path.append(os.path.abspath('../env'))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, event, exc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapper
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from base import Base
from stringUtilities import stripWhiteSpace,stripSlash

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
            target.fileName = stripSlash(stripWhiteSpace(target.fileName))
        if (target.fileDir is not None):
            target.fileDir = stripWhiteSpace(target.fileDir)
        

#Process filename and dir before inserting
listen(File, 'before_insert', File._stripFileNameDir)
listen(File, 'before_update', File._stripFileNameDir)