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
	Session.commit()
	for j in xml.findall('Job'):
		thisJob = __createModel(Job,j)
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

def __createModel(modelObj,m):
	attrDict = {}
	print("Creating a "+modelObj.__name__)
	for attr in modelObj.__table__.columns._data.keys()[1:]:
		value = m.findtext(attr)
		if value is not None:
			print(attr+": "+value)
			attrDict[attr] = value
	if (attrDict):
		model = modelObj(**attrDict)
		return model
	else:
		return None

def __updateModel(modelObj,m):
	modelToUpdate = m.findtext(modelObj.__name__)
	try:
		mID = int(modelToUpdate)
		model = Session.query(Model).get(mID)
	except ValueError:
		try:
			model = Session.query(Model).filter(Model.name.like(modelToUpdate)).one()
		except ormexc.MultipleResultsFound:
			print("More than one "+model.__name__+" of that name found. Please specify by ID.")
			for mod in Session.query(Model).filter(Model.name.like(modelToUpdate)).one():
				print mod.name, mod.id
			return None
	print("Patching "+model.__name__+" "+model.name+" id: "+str(model.id))
	for attr in model.__table__.columns._data.keys()[1:]:
		value = c.findtext(attr)
		if (value is not None):
			print("Setting "+attr+" to "+value)
			setattr(model, attr, value)
	return model

def __deleteModel(modelObj,m):
	modelToDelete = m.findtext(modelObj.__name__)
	try:
		mID = int(modelToDelete)
		model = Session.query(Model).get(mID)
	except ValueError:
		try:
			model = Session.query(Model).filter(Model.name.like(modelToUpdate)).one()
		except ormexc.MultipleResultsFound:
			print("More than one "+model.__name__+" of that name found. Please specify by ID.")
			for mod in Session.query(Model).filter(Model.name.like(modelToUpdate)).one():
				print mod.name, mod.id
			return None
		except ormexc.NoResultFound:
			print("No "+model.__name__+" of that name or id found. It may have been cascade deleted already.")
			return None
	except ormexc.NoResultFound:
		print("No "+model.__name__+" of that name or id found. It may have been cascade deleted already.")
		return None
	print("Deleting "+model.name+" "+str(model.id))
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
