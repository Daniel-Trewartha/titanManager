import xml.etree.ElementTree as ET
import os

campaign = ET.Element("Campaign")
ET.SubElement(campaign,"campaignName").text = 'Test'
ET.SubElement(campaign,"wallTime").text = '00:10:00'
ET.SubElement(campaign,"checkWallTime").text = '00:10:00'
header = "import wraprun"
footer = ""
checkHeader = "import wraprun"
checkFooter = ""
ET.SubElement(campaign,"header").text = header
ET.SubElement(campaign,"footer").text = footer
ET.SubElement(campaign,"checkHeader").text = checkHeader
ET.SubElement(campaign,"checkFooter").text = checkFooter

tree = ET.ElementTree(campaign)
tree.write("testCampaign.xml")