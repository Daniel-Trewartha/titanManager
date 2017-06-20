import xml.etree.ElementTree as ET
import os

job = ET.Element("Job")
ET.SubElement(job,"jobname").text = 'testJob'
ET.SubElement(job,"nodes").text = str(1)
ET.SubElement(job,"wallTime").text = '00:10:00'
ET.SubElement(job,"executionCommand").text = "pwd"
ET.SubElement(job,"outputCheckCommand").text = "pwd"
ET.SubElement(job,"outputCheckLoc").text = os.path.abspath(__file__)
ET.SubElement(job,"campaign").text = "Test"
iF = ET.SubElement(job,'inputFiles')
iF1 = ET.SubElement(iF,'elem')
ET.SubElement(iF1,'filename').text = 'test.xml'
ET.SubElement(iF1,'directory').text = os.path.split(os.path.abspath(__file__))[0]
iF2 = ET.SubElement(iF,'elem')
ET.SubElement(iF2,'filename').text = 'nonexistent.xml'
ET.SubElement(iF2,'directory').text = os.path.split(os.path.abspath(__file__))[0]
oF = ET.SubElement(job,'outputFiles')
oF1 = ET.SubElement(oF,'elem')
ET.SubElement(oF1,'filename').text = 'output.txt'
ET.SubElement(oF1,'directory').text = os.path.split(os.path.abspath(__file__))[0]

tree = ET.ElementTree(job)
tree.write("testJob.xml")