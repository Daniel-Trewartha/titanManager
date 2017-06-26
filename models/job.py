#Remove dependency on jobFile - use files attribute instead
import datetime, os, sys, subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'..')))
from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON, event, ForeignKey
from sqlalchemy.orm import relationship, mapper, joinedload
from sqlalchemy.inspection import inspect
from sqlalchemy.event import listen
from src.base import Base
from env.environment import virtualEnvPath, jobStatusManagerPath
from src.stringUtilities import stripWhiteSpace,stripSlash,parseTimeString

class Job(Base):
    __tablename__ = 'jobs'
    __name__ = 'job'
        
    id = Column(Integer, primary_key=True)
    name = Column('name',String,default='default')
    executionCommand = Column('executionCommand',String,default="serial echo 'No Execution Command'")
    nodes = Column('nodes',Integer,default=1)
    wallTime = Column('wallTime',Interval,default=datetime.timedelta(hours=1))
    status = Column('status',String)
    pbsID = Column('pbsID',Integer)
    files = relationship("File", back_populates="job",cascade="all, delete-orphan")
    campaignID = Column('campaignID',Integer,ForeignKey("campaigns.id"))
    campaign = relationship("Campaign", back_populates="jobs")

    numFails = Column('numFails',Integer)

    #successful completion of a job marked in two ways
    #existence of output files(if any)
    #running of an output check code
    #output check code should produce a single file in checkOutLoc, the contents of which are either 'True' or 'False'
    checkOutputScript = Column('checkOutputScript',String)
    checkNodes = Column('checkNodes',Integer,default=1)
    checkWallTime = Column('checkWallTime',Interval,default=datetime.timedelta(hours=1))
    checkPbsID = Column('checkPbsID',Integer)
    checkOutputLoc = Column('checkOutLoc',String)

    #Public methods

    def checkCompletionStatus(self,Session):
        #Check if job has run successfully
        if (self.__checkOut(Session) and self.__checkOutputFiles(Session)):
            return True
        else:
            return False

    def checkInput(self,Session):
        #check for input file existence
        for iF in [iF for iF in self.files if iF.ioType == 'input']:
            if (not iF.exists(Session)):
                return False
        return True

    #Private methods

    def __checkOut(self,Session):
        #check the output file in checkOutLoc
        #if no output file specified, return true
        if (self.checkOutputLoc is not None):
            if (os.path.exists(self.checkOutputLoc)):
                with open(self.checkOutputLoc,'r') as f:
                    return f.read()
            else:
                return False

        else:
            return True

    def __checkOutputFiles(self,Session):
        #check for output file existence
        #returns true if job has no output files
        for oF in [oF for oF in self.files if oF.ioType == 'output']:
            if (not oF.exists(Session)):
                return False
        return True

    @staticmethod
    def _stripJobName(mapper, connection, target):
        if (target.name is not None):
            target.name = stripSlash(stripWhiteSpace(target.name))
        if (target.checkOutputLoc is not None):
            target.checkOutputLoc = stripWhiteSpace(target.checkOutputLoc)

    @staticmethod
    def _parseWallTime(mapper, connection, target):
        if (target.wallTime is not None):
            target.wallTime = parseTimeString(str(target.wallTime))
        if (target.checkWallTime is not None):
            target.checkWallTime = parseTimeString(str(target.checkWallTime))
#EVENT LISTENERS

#Defaults for attributes that should not be settable at initialization
@event.listens_for(Job,"init")
def init(target, args, kwargs):
    target.status = "Accepted"
    target.pbsID = None
    target.numFails = 0
    target.checkPbsID = None

#Process jobname before inserting
listen(Job, 'before_insert', Job._stripJobName)
listen(Job, 'before_update', Job._stripJobName)
#Process walltime and checkwalltime
listen(Job, 'before_insert', Job._parseWallTime)
listen(Job, 'before_update', Job._parseWallTime)