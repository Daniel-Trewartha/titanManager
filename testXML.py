import xml.etree.ElementTree as ET
import os

job = ET.Element("Job")
jobname = ET.SubElement(job,"jobname").text = 'testJob'
nodes = ET.SubElement(job,"nodes").text = str(1)
walltime = ET.SubElement(job,"wallTime").text = '00:10:00'
eC = ET.SubElement(job,"executionCommand").text = "pwd"
iF = ET.SubElement(job,'inputFiles')
iF1 = ET.SubElement(iF,'elem')
iF1name = ET.SubElement(iF1,'filename').text = 'test.xml'
iF1dir = ET.SubElement(iF1,'directory').text = os.path.split(os.path.abspath(__file__))[0]
iF2 = ET.SubElement(iF,'elem')
ET.SubElement(iF2,'filename').text = 'nonexistent.xml'
ET.SubElement(iF2,'directory').text = os.path.split(os.path.abspath(__file__))[0]
oF = ET.SubElement(job,'outputFiles')
oF1 = ET.SubElement(oF,'elem')
ET.SubElement(oF1,'filename').text = 'output.txt'
ET.SubElement(oF1,'directory').text = os.path.split(os.path.abspath(__file__))[0]

tree = ET.ElementTree(job)
tree.write("test.xml")