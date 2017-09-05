import datetime, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, Boolean, event, exc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapper
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from src.base import Base
from src.stringUtilities import stripWhiteSpace,stripSlash
from env.environment import cluster
from src.globusUtilities import transferFile

class File(Base):
    __tablename__ = 'files'
    __name__ = 'file'
        
    id = Column(Integer, primary_key=True)
    name = Column('name',String,nullable=False)
    fileDir = Column('fileDir',String,nullable=False)
    #Job this file is associated with
    jobID = Column('jobID',Integer,ForeignKey("jobs.id"),nullable=False)
    #Whether this is an input or an output file
    ioType = Column('ioType',String,default="output")
    job = relationship("Job", back_populates="files")

    #Globus attributes
    #The globus id of the file's location
    location = Column('location',String,default=cluster)
    #The number of times a stage in has been attempted for this file
    stageInAttempts = Column('stageInAttempts',Integer,default=0)
    #Whether a local copy of this should be retained after the job is complete
    retainLocalCopy = Column('retainLocalCopy',Boolean,default=True)
    #The globus id this file should be staged out to after job is complete
    stageOutLocation = Column('stageOutLocation',String,nullable=True)
    #The folder this file should be staged out to after this job is complete
    stageOutDir = Column('stageOutDir',String,nullable=True)

    def filePath(self):
        return os.path.join(self.fileDir,self.name)

    def exists(self,Session):
        if (os.path.exists(self.filePath())):
            return True
        else:
            return False

    def local(self,Session):
        #True if file is supposed to exist locally
        if (self.location == cluster):
            return True
        else:
            return False

    def remove(self,Session):
        if self.exists(Session):
            os.remove(self.filePath())
            return True
        else:
            return False

    def stageIn(self,Session,direc):
        transferFile(self.name,direc,cluster,self.fileDir,self.location)

    def stageOut(self,Session):
        transferFile(self.name,self.stageOutDir,self.stageOutLocation,self.fileDir,cluster)

    @staticmethod
    def _stripFileNameDir(mapper, connection, target):
        if (target.name is not None):
            target.name = stripSlash(stripWhiteSpace(target.name))
        if (target.fileDir is not None):
            target.fileDir = stripWhiteSpace(target.fileDir)
        

#Process filename and dir before inserting
listen(File, 'before_insert', File._stripFileNameDir)
listen(File, 'before_update', File._stripFileNameDir)

#Defaults for attributes that should not be settable at initialization
@event.listens_for(File,"init")
def init(target, args, kwargs):
    target.stageInAttempts = 0
