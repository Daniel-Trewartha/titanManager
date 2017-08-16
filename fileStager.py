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
def stager(fileList,Session):
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

if __name__ == '__main__':
    with session_scope(engine) as Session:
        Base.metadata.create_all(engine)
        if(len(sys.argv)==2):
        	stager(sys.argv[1],Session)
        else:
            print("File Stager")
