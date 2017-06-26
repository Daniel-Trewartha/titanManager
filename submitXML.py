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
	for c in xml.findall('Campaign'):
		thisCampaign = __createModel(Campaign,c)
		Session.add(thisCampaign)
		Session.commit()
	for j in xml.findall('Job'):
		thisJob = __createModel(Job,j)
		Session.add(thisJob)
		Session.commit()
		for iF in j.find('inputFiles').findall('elem'):
			thisFile = __createFile(iF,'input',thisJob.id)
			Session.add(thisFile)
		for oF in j.find('outputFiles').findall('elem'):
			thisFile = __createFile(oF,'output',thisJob.id)
			Session.add(thisFile)
		Session.commit()

def patchXML(xml):
	for campaign in xml.findall('Campaign'):
		__updateModel(Campaign,campaign)
	for job in xml.findall('Job'):
		__updateJob(job)
	for f in xml.findall('File'):
		__updateFile(f)

def deleteXML(xml):
	for c in xml.findall('Campaign'):
		campaignName = c.findtext('name')
		try:
			cID = int(campaignName)
			campaign = Session.query(Campaign).get(cID)
		except ValueError:
			campaign = Session.query(Campaign).filter(Campaign.name.like(campaignName)).one()
		print("Deleting "+campaign.name)
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

def __createFile(f,ioType,jobID):
	file = __createModel(File,f)
	file.ioType = ioType
	file.jobID = jobID
	print("ioType: "+ioType)
	print("jobID: "+str(jobID))
	return file

def __createModel(modelObj,m):
	attrDict = {}
	print("Creating a "+modelObj.__name__)
	for attr in modelObj.__table__.columns._data.keys()[1:]:
		value = m.findtext(attr)
		if value is not None:
			print(attr+": "+value)
			attrDict[attr] = value
		model = modelObj(**attrDict)
	return model

def __updateModel(modelObj,m):
	modelToUpdate = m.findtext(model.__name__)
	try:
		mID = int(modelToUpdate)
		model = Session.query(Model).get(mID)
	except ValueError:
		model = Session.query(Model).filter(Model.name.like(modelToUpdate)).one()
	print("Patching "+model.__name__+" "+model.name+" id: "+str(model.id))
	for attr in model.__table__.columns._data.keys()[1:]:
		value = c.findtext(attr)
		if (value is not None):
			print("Setting "+attr+" to "+value)
			setattr(model, attr, value)
	return model

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