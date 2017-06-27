import xml.etree.ElementTree as ET
import os

data = ET.Element("Data")
campaign = ET.SubElement(data,"Campaign")
ET.SubElement(campaign,"campaignName").text = 'Testtest'
ET.SubElement(campaign,"campaign").text = 'Test'

tree = ET.ElementTree(data)
tree.write("testPatchXML.xml")
