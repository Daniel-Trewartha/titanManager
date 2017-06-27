import xml.etree.ElementTree as ET
import os

#An example script to delete data from the database
#Here we delete one of the jobs from the example campaign
#and one of the input files from the other job
data = ET.Element("Data")
job1 = ET.SubElement(data,"Job")
ET.SubElement(job1,"name").text = 'testJob1'
file = ET.SubElement(data,"File")
ET.SubElement(file,"name").text = 'testJob2Executable.data'

tree = ET.ElementTree(data)
tree.write("exampleDeleteXML.xml")
