import xml.etree.ElementTree as ET
import os

#Create a demonstration 'test' campaign with two jobs
data = ET.Element("Data")
campaign = ET.SubElement(data,"Campaign")
ET.SubElement(campaign,"name").text = 'Test'
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

job1 = ET.SubElement(data,"Job")
ET.SubElement(job1,"name").text = 'testJob1'
ET.SubElement(job1,"nodes").text = str(1)
ET.SubElement(job1,"wallTime").text = '00:10:00'
ET.SubElement(job1,"executionCommand").text = "serial pwd"
#ET.SubElement(job1,"outputCheckCommand").text = "serial echo \'True\' >> "+os.path.join(os.path.split(os.path.abspath(__file__))[0],'testJob1Check.txt')
ET.SubElement(job1,"outputCheckCommand").text = "serial pwd"
ET.SubElement(job1,"outputCheckLoc").text = os.path.join(os.path.split(os.path.abspath(__file__))[0],'testJob1Check.txt')
ET.SubElement(job1,"campaign").text = "Test"
iF = ET.SubElement(job1,'inputFiles')
iF1 = ET.SubElement(iF,'elem')
ET.SubElement(iF1,'name').text = 'test.xml'
ET.SubElement(iF1,'fileDir').text = os.path.split(os.path.abspath(__file__))[0]
iF2 = ET.SubElement(iF,'elem')
ET.SubElement(iF2,'name').text = 'nonexistent.xml'
ET.SubElement(iF2,'fileDir').text = os.path.split(os.path.abspath(__file__))[0]
oF = ET.SubElement(job1,'outputFiles')
oF1 = ET.SubElement(oF,'elem')
ET.SubElement(oF1,'name').text = 'output.txt'
ET.SubElement(oF1,'fileDir').text = os.path.split(os.path.abspath(__file__))[0]

job2 = ET.SubElement(data,"Job")
ET.SubElement(job2,"name").text = 'testJob2'
ET.SubElement(job2,"nodes").text = str(1)
ET.SubElement(job2,"wallTime").text = '00:10:00'
ET.SubElement(job2,"executionCommand").text = "pwd"
#ET.SubElement(job2,"outputCheckCommand").text = "serial echo \'True\' >> "+os.path.join(os.path.split(os.path.abspath(__file__))[0],'testJob2Check.txt')
ET.SubElement(job1,"outputCheckCommand").text = "serial pwd"
ET.SubElement(job2,"outputCheckLoc").text = os.path.join(os.path.split(os.path.abspath(__file__))[0],'testJob2Check.txt')
ET.SubElement(job2,"campaign").text = "Test"
iF = ET.SubElement(job2,'inputFiles')
iF1 = ET.SubElement(iF,'elem')
ET.SubElement(iF1,'name').text = 'test.xml'
ET.SubElement(iF1,'fileDir').text = os.path.split(os.path.abspath(__file__))[0]
iF2 = ET.SubElement(iF,'elem')
ET.SubElement(iF2,'name').text = 'nonexistent.xml'
ET.SubElement(iF2,'fileDir').text = os.path.split(os.path.abspath(__file__))[0]
oF = ET.SubElement(job2,'outputFiles')
oF1 = ET.SubElement(oF,'elem')
ET.SubElement(oF1,'name').text = 'output.txt'
ET.SubElement(oF1,'fileDir').text = os.path.split(os.path.abspath(__file__))[0]


tree = ET.ElementTree(data)
tree.write("testXML.xml")
