import os, time, sys
import xml.etree.ElementTree as ET
from models.job import Job
from models.jobFile import File
from models.campaign import Campaign
from src.base import Base, session_scope, engine
from src.stringUtilities import parseTimeString
from sqlalchemy import exc

def main():
	print("Extracting from "+sys.argv[1])
	xml = ET.parse(sys.argv[1])
	for campaign in xml.findall('Campaign'):
		parseCampaign(campaign)
	for job in xml.findall('Job'):
		parseJob(job)

def parseCampaign(campaign):
	campaignName = campaign.find('campaignName').text
	header = campaign.find('header').text
	footer = campaign.find('footer').text
	checkHeader = campaign.find('checkHeader').text
	checkFooter = campaign.find('checkFooter').text
	wallTime = parseTimeString(campaign.find('wallTime').text)
	checkWallTime = parseTimeString(campaign.find('checkWallTime').text)
	campaignObj = Campaign(campaignName=campaignName,wallTime=wallTime,header=header,footer=footer,checkHeader=checkHeader,checkFooter=checkFooter,checkWallTime=checkWallTime)
	try:
		Session.add(campaignObj)
		Session.commit()
		print("Campaign details: ")
		print("Campaign name: " + campaignObj.campaignName)
		print("header: " + str(campaignObj.header))
		print("footer: " + str(campaignObj.footer))
		print("check header: " + str(campaignObj.checkHeader))
		print("check footer: " + str(campaignObj.checkFooter))
		print("walltime: " + str(campaignObj.wallTime))
		print("check wall time: " + str(campaignObj.checkWallTime))
	except exc.IntegrityError:
		Session.rollback()
		print("A campaign of this name already exists")

def parseJob(job):
	jobName = job.find('jobname').text
	nodes = int(job.find('nodes').text)
	wallTime = parseTimeString(job.find('wallTime').text)
	eC = job.find('executionCommand').text
	cC = job.find('outputCheckCommand').text
	cOutLoc = job.find('outputCheckLoc').text
	campaign = job.find('campaign').text
	try:
		cID = int(campaign)
	except ValueError:
		cID = Session.query(Campaign).filter(Campaign.campaignName.like(campaign)).one().id
	jobObj = Job(jobName=jobName,nodes=nodes,wallTime=wallTime,executionCommand=eC,checkOutputScript=cC,checkOutputLoc=cOutLoc,campaignID=cID)
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
		print(os.path.join(iFs[-1].fileDir,iFs[-1].fileName))
	oFs = []
	print("Output Files: ")
	for oF in job.find('outputFiles').findall('elem'):
		name = oF.find('filename').text
		directory = oF.find('directory').text
		oFs.append(File(fileName=name,fileDir=directory,ioType='output',jobID=jobObj.id))
		Session.add(oFs[-1])
		print(os.path.join(oFs[-1].fileDir,oFs[-1].fileName))
	jobObj.files = iFs+oFs
	Session.commit()
	for iF in iFs:
		if (not iF.exists(Session)):
			print("Warning: input file "+os.path.join(iF.fileDir,iF.fileName)+" does not exist")

if __name__ == '__main__':
	if (len(sys.argv) == 2):
		with session_scope(engine) as Session:
			Base.metadata.create_all(engine)
			main()
	else:
		print("Submit name of xml file")