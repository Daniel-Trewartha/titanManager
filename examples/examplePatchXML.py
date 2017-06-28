import xml.etree.ElementTree as ET
import os
#An example script to edit data in the database
#This script edits the header and name of the campaign we created in the submission xml
#And the nodes of one of the jobs
data = ET.Element("Data")
campaign = ET.SubElement(data,"Campaign")
ET.SubElement(campaign,"Campaign").text = 'Test'
ET.SubElement(campaign,"name").text = 'PatchedTest'
ET.SubElement(campaign,"header").text = 'import wraprun \n module load python'

job = ET.SubElement(data,"Job")
ET.SubElement(job,"Job").text = 'testJob1'
ET.SubElement(job,"nodes").text = str(2)

tree = ET.ElementTree(data)
tree.write("examplePatchXML.xml")
