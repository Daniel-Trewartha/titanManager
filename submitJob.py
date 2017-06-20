# a little executable for submitting a job to
# takes job name as argument

import os, time, sys
import xml.etree.ElementTree as ET
from models.job import Job
from models.jobFile import File
from src.base import Base, session_scope, engine
from src.jobOps import submitJobs, rerunFailedJobs, bundleJobs, checkJobsStatus, checkInputFiles
from src.stringUtilities import parseTimeString

def main():

	#A job has: a name
	#a number of nodes
	#a walltime
	#an execution command
	#a list of required input files
	#a list of expected output files

	#A file has:
	#a name
	#a directory
	print("Extracting job from "+sys.argv[1])
	xml = ET.parse(sys.argv[1])
	job = xml.getroot()
	jobName = job.find('jobname').text
	nodes = int(job.find('nodes').text)
	wallTime = parseTimeString(job.find('wallTime').text)
	eC = job.find('executionCommand').text
	jobObj = Job(jobName=jobName,nodes=nodes,wallTime=wallTime,executionCommand=eC)
	Session.add(jobObj)
	Session.commit()
	print("Job details: ")
	print("Jobname: " + jobObj.jobName)
	print("Nodes: " + str(jobObj.nodes))
	print("Wall Time: " + str(jobObj.wallTime))
	print("Execution Command: " + jobObj.executionCommand)
	iFs = []
	print("Input Files: ")
	for iF in job.find('inputFiles').findall('elem'):
		name = iF.find('filename').text
		directory = iF.find('directory').text
		iFs.append(File(fileName=name,fileDir=directory,ioType='input',jobID=jobObj.id))
		Session.add(iFs[-1])
		print(os.path.join(iFs[-1].fileDir,iFs[-1].fileDir))
	oFs = []
	print("Output Files: ")
	for oF in job.find('outputFiles').findall('elem'):
		name = oF.find('filename').text
		directory = oF.find('directory').text
		oFs.append(File(fileName=name,fileDir=directory,ioType='output',jobID=jobObj.id))
		Session.add(oFs[-1])
		print(os.path.join(oFs[-1].fileDir,oFs[-1].fileDir))
	jobObj.files = iFs+oFs
	Session.commit()
	for iF in iFs:
		if (not iF.exists(Session)):
			print("Warning: input file "+os.path.join(iF.fileDir,iF.fileName)+" does not exist")
	print("Job added to database")

if __name__ == '__main__':
	if (len(sys.argv) == 2):
		with session_scope(engine) as Session:
			Base.metadata.create_all(engine)
			main()
	else:
		print("Submit name of xml file with job details")