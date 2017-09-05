#This is where the stager will be implemented
#It will take a list of file ids in
#Then try to stage them

import sys
from models.jobFile import File
from models.job import Job
from models.campaign import Campaign
from src.base import Base,session_scope,engine
from env.environment import cluster,inputDir,maxStageIns

#Given a list of files, launch the stage-in process for each
def stageIn(fileList,Session):
	for f in fileList:
		thisFile = Session.query(File).get(int(f))
		if (thisFile):
			if (thisFile.stageInAttempts < maxStageIns):
				thisFile.stageInAttempts += 1
				Session.commit()
				thisFile.stageIn(Session,inputDir)
				thisFile.fileDir = inputDir
				if (thisFile.exists(Session)):
					thisFile.location = cluster
					Session.commit()
				else:
					Session.rollback()
			else:
				thisFile.job.status = "Missing Input"
				Session.commit()

#Given a list of files, launch the stage-out process for each
def stageOut(fileList,Session):
	for f in fileList:
		thisFile = Session.query(File).get(int(f))
		if (thisFile):
			thisFile.stageOut(Session)
			if (not thisFile.exists(Session)):
				thisFile.location = thisFile.stageOutLocation
				thisFile.fileDir = thisFile.stageOutDir
				Session.commit()
			else:
				Session.rollback()

if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        if(len(sys.argv)==3):
        	if(sys.argv[1] == 'In'):
	        	stageIn(sys.argv[2],Session)
	        elif(sys.argv[1] == 'Out'):
	        	stageOut(sys.argv[2],Session)
        else:
            print("File Stager")
