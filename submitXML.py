import os, time, sys
import xml.etree.ElementTree as ET
from models.job import Job
from models.jobFile import File
from models.campaign import Campaign
from src.base import Base, session_scope, engine
from src.stringUtilities import parseTimeString
from sqlalchemy import exc
from sqlalchemy.orm import exc as ormexc
from sqlalchemy.orm import class_mapper
from src.stringUtilities import stripWhiteSpace,stripSlash

def postXML(xml):
	for campaign in xml.findall('Campaign'):
		__createCampaign(campaign)
	for job in xml.findall('Job'):
		__createJob(job)

def patchXML(xml):
	print "This functionality is not yet available"
	#for campaign in xml.findall('Campaign'):
	#	__updateCampaign(campaign)
	#for job in xml.findall('Job'):
	#	__updateJob(job)
	#for f in xml.findall('File'):
	#	__updateFile(f)

def deleteXML(xml):
	for c in xml.findall('Campaign'):
		campaignName = c.findtext('campaignName')
		try:
			cID = int(campaignName)
			campaign = Session.query(Campaign).get(cID)
		except ValueError:
			campaign = Session.query(Campaign).filter(Campaign.campaignName.like(campaignName)).one()
		print("Deleting "+campaign.campaignName)
		Session.delete(campaign)
	Session.commit()
	for j in xml.findall('Job'):
		jobName = j.findtext('jobName')
		try:
			jId = int(jobName)
			try:
				job = Session.query(Job).get(jId)
			except exc.NoResultFound:
				print ("No Job of that name found. Perhaps it was already deleted with its parent campaign.")
				continue

		except ValueError:
			try:
				job = Session.query(Job).filter(Job.jobName.like(jobName)).one()
			except ormexc.MultipleResultsFound:
				print ("More than one job of that name found. Please specify by ID.")
				for job in Session.query(Job).filter(Job.jobName.like(jobName)).all():
					print(job.jobName,job.ID)
				continue
			except ormexc.NoResultFound:
				print ("No Job of that name found. Perhaps it was already deleted with its parent campaign.")
				continue
		print("Deleting "+job.jobName)
		Session.delete(job)
	Session.commit()
	for f in xml.findall("File"):
		fileName = f.findtext('fileName')
		try:
			fId = int(fileName)
			try:
				file = Session.query(File).get(fId)
			except exc.NoResultFound:
				print ("No file of that name found. Perhaps it was already deleted with its parent job.")
				continue

		except ValueError:
			try:
				file = Session.query(File).filter(File.fileName.like(fileName)).one()
			except ormexc.MultipleResultsFound:
				print ("More than one file of that name found. Please specify by ID.")
				for file in Session.query(File).filter(File.fileName.like(fileName)).all():
					print(file.jobName,file.ID)
				continue
			except ormexc.NoResultFound:
				print ("No file of that name found. Perhaps it was already deleted with its parent job.")
				continue
		print("Deleting "+file.fileName)
		Session.delete(file)
	Session.commit()

def __createCampaign(campaign):
	campaignName = campaign.find('campaignName').text
	header = campaign.findtext('header')
	footer = campaign.findtext('footer')
	checkHeader = campaign.findtext('checkHeader')
	checkFooter = campaign.findtext('checkFooter')
	wallTime = parseTimeString(campaign.findtext('wallTime'))
	checkWallTime = parseTimeString(campaign.findtext('checkWallTime'))
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

def __updateCampaign(c):
	campaignName = c.findtext('campaignName')
	try:
		cID = int(campaignName)
		campaign = Session.query(Campaign).get(cID)
	except ValueError:
		campaign = Session.query(Campaign).filter(Campaign.campaignName.like(campaignName)).one()
	for attr in campaign.__table__.columns._data.keys()[1:]:
		value = c.findtext(attr)
		if (value is not None):
			print eval("campaign."+stripSlash(stripWhiteSpace(attr)))
			eval("campaign."+stripSlash(stripWhiteSpace(attr))+" = \""+value+"\"")
			print eval("campaign."+stripSlash(stripWhiteSpace(attr)))

def __createJob(job):
	jobName = job.findtext('jobname')
	nodes = int(job.findtext('nodes'))
	wallTime = parseTimeString(job.findtext('wallTime'))
	eC = job.findtext('executionCommand')
	cC = job.findtext('outputCheckCommand')
	cN = job.findtext('cN')
	cOutLoc = job.findtext('outputCheckLoc')
	campaign = job.findtext('campaign')
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
	with session_scope(engine) as Session:
		Base.metadata.create_all(engine)
		if (len(sys.argv) == 3):
			print("Extracting from "+sys.argv[2])
			xml = ET.parse(sys.argv[2])
			if (sys.argv[1] == 'Post'):
				postXML(xml)
			elif (sys.argv[1] == 'Patch'):
				patchXML(xml)
			elif (sys.argv[1] == 'Delete'):
				deleteXML(xml)
		else:
			print("Submit name of xml file")