import datetime, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, event, exc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapper
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from src.base import Base
from src.stringUtilities import stripWhiteSpace,stripSlash

class File(Base):
    __tablename__ = 'files'
        
    id = Column(Integer, primary_key=True)
    fileName = Column('fileName',String,nullable=False)
    fileDir = Column('fileDir',String,nullable=False)
    jobID = Column('jobID',Integer,ForeignKey("jobs.id"),nullable=False)
    ioType = Column('ioType',String,default="output")
    job = relationship("Job", back_populates="Files")

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
