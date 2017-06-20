# a little executable for submitting a campaign to
# takes campaign name as argument

import os, time, sys
import xml.etree.ElementTree as ET
from models.job import Job
from models.jobFile import File
from models.campaign import Campaign
from src.base import Base, session_scope, engine
from src.stringUtilities import parseTimeString

def main():

	#A campaign has: a name
	#a header
	#a footer
	# a check  header
	#a check footer
	#a walltime
	#a check walltime

	print("Extracting campaign from "+sys.argv[1])
	xml = ET.parse(sys.argv[1])
	campaign = xml.getroot()
	campaignName = campaign.find('campaignName').text
	header = campaign.find('header').text
	footer = campaign.find('footer').text
	checkHeader = campaign.find('checkHeader').text
	checkFooter = campaign.find('checkFooter').text
	wallTime = parseTimeString(campaign.find('wallTime').text)
	checkWallTime = parseTimeString(campaign.find('checkWallTime').text)
	campaignObj = Campaign(campaignName=campaignName,wallTime=wallTime,header=header,footer=footer,checkHeader=checkHeader,checkFooter=checkFooter,checkWallTime=checkWallTime)
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
	print("Campaign added to database")

if __name__ == '__main__':
	if (len(sys.argv) == 2):
		with session_scope(engine) as Session:
			Base.metadata.create_all(engine)
			main()
	else:
		print("Submit name of xml file with campaign details")