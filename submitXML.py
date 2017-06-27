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
		if (thisCampaign is not None):
			Session.add(thisCampaign)
			try:
				Session.commit()
			except exc.IntegrityError:
				Session.rollback()
				print ("A campaign of name "+thisCampaign.name+" already exists")
	for j in xml.findall('Job'):
		thisJob = __createJob(Job,j)
		if (thisJob is not None):
			Session.add(thisJob)
			Session.commit()
			for iF in j.find('inputFiles').findall('elem'):
				thisFile = __createFile(iF,'input',thisJob.id)
				if (thisFile is not None):
					Session.add(thisFile)
			for oF in j.find('outputFiles').findall('elem'):
				thisFile = __createFile(oF,'output',thisJob.id)
				if (thisFile is not None):
					Session.add(thisFile)
			Session.commit()

def patchXML(xml):
	for campaign in xml.findall('Campaign'):
		thisCampaign = __updateModel(Campaign,campaign)
	for job in xml.findall('Job'):
		thisJob = __updateModel(job)
		if (thisJob is not None):
			for iF in j.find('inputFiles').findall('elem'):
				thisFile = __createFile(iF,'input',thisJob.id)
				if (thisFile is not None):
					Session.add(thisFile)
			for oF in j.find('outputFiles').findall('elem'):
				thisFile = __createFile(oF,'output',thisJob.id)
				if (thisFile is not None):
					Session.add(thisFile)
	for f in xml.findall('File'):
		__updateModel(f)
	Session.commit()

def deleteXML(xml):
	for campaign in xml.findall('Campaign'):
		m = __deleteModel(Campaign,campaign)
		if (m is not None):
			Session.delete(m)
	for job in xml.findall('Job'):
		m = __deleteModel(job)
		if (m is not None):
			Session.delete(m)
	for f in xml.findall('File'):
		m = __deleteModel(f)
		if (m is not None):
			Session.delete(m)
	Session.commit()

def __createFile(f,ioType,jobID):
	file = __createModel(File,f)
	file.ioType = ioType
	file.jobID = jobID
	print("ioType: "+ioType)
	print("jobID: "+str(jobID))
	return file

def __createJob(jobObj,j):
	job = __createModel(jobObj,j)
	cID = j.findtext('campaign')
	if (cID):
		campaign = __findModel(Campaign, cID)
		if (campaign is not None):
			job.campaignID = campaign.id
			print("campaignID: "+str(campaign.id))
	return job

def __createModel(modelObj,m):
	print("Creating a "+modelObj.__name__)
	name = m.findtext('name')
	if name is not None:
		model = modelObj(name=name)
		for attr in modelObj.__table__.columns._data.keys()[1:]:
			value = m.findtext(attr)
			if value is not None:
				print(attr+": "+value)
				setattr(model, attr, value)
		return model
	else:
		return None

def __updateModel(modelObj,m):
	modelToUpdate = m.findtext(modelObj.__name__)
	model = __findModel(modelObj,modelToUpdate)
	if (model is not None):
		print("Patching "+modelObj.__name__+" "+model.name+" id: "+str(model.id))
		for attr in modelObj.__table__.columns._data.keys()[1:]:
			value = c.findtext(attr)
			if (value is not None):
				print("Setting "+attr+" to "+value)
				setattr(model, attr, value)
		return model
	else:
		return None

def __deleteModel(modelObj,m):
	modelToDelete = m.findtext(modelObj.__name__)
	model = __findModel(modelObj,modelToDelete)
	if (model is not None):
		print("Deleting "+modelObj.name+" "+str(model.name)+" id: "+str(model.id))
		return model
	else:
		return None

def __findModel(modelObj,key):
#Find a model of kind modelObj using a key, which may either be its name or its id
#Returns none if it cannot local either
	try:
		mId = int(key)
		model = Session.query(modelObj).get(mID)
	except ValueError:
		try:
			model = Session.query(modelObj).filter(modelObj.name.like(key)).one()
		except ormexc.MultipleResultsFound:
			print ("More than one "+modelObj.__name__+" of that name found. Please specify by ID.")
			for m in Session.query(modelObj).filter(modelObj.name.like(key)).one():
				print m.name, m.id
			return None
		except ormexc.NoResultFound:
			print ("No "+modelObj.__name__+" with name "+str(key)+" found.")
			return None
	except ormexc.NoResultFound:
		print ("No "+modelObj.__name__+" with id "+str(key)+" found.")
		return None
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
