import xml.etree.ElementTree as ET
import os

#Create a demonstration 'test' campaign with two jobs
#Mandatory fields for a campaign - name
data = ET.Element("Data")
campaign = ET.SubElement(data,"Campaign")
#Campaign names are unique, should not contain white space
ET.SubElement(campaign,"name").text = 'Test'
#Campaign can have a wall time - if it does not infer one from the jobs
ET.SubElement(campaign,"wallTime").text = '00:10:00'
ET.SubElement(campaign,"checkWallTime").text = '00:10:00'
#headers and footers for pbs submission scripts
header = "import wraprun"
footer = ""
checkHeader = "import wraprun"
checkFooter = ""
ET.SubElement(campaign,"header").text = header
ET.SubElement(campaign,"footer").text = footer
ET.SubElement(campaign,"checkHeader").text = checkHeader
ET.SubElement(campaign,"checkFooter").text = checkFooter

#Create a job
#Mandatory fields for a job - name, campaign
workDir = "/lustre/atlas/scratch/danieltr/nph103"
output = 'testJob1.out'
checkOutput = 'testJob1Check.out'
job1 = ET.SubElement(data,"Job")
ET.SubElement(job1,"name").text = 'testJob1'
#Nodes for execution and check jobs
ET.SubElement(job1,"checkNodes").text = str(1)
ET.SubElement(job1,"nodes").text = str(1)
#Walltimes overriden by campaign walltime unless campaign does not have one
ET.SubElement(job1,"checkWallTime").text = '00:10:00'
ET.SubElement(job1,"wallTime").text = '00:10:00'
#Command to be executed with wraprun
#test Job creates a file at workDir
#Note use of serial for a non-MPI call
ET.SubElement(job1,"executionCommand").text = "serial echo 'testJob1 Successful' > "+os.path.join(workDir,output)
#Check command to be executed with wraprun
#test Job's check copies the contents of the output file verbatim
ET.SubElement(job1,"outputCheckCommand").text = "serial cp "+os.path.join(workDir,output)+" "+os.path.join(workDir,checkOutput)
#Front end script to verify the output of checker
#Should write True or False to stdout
#test Job greps 'Successful' in the expected check output location
#Python evaluates any non-empty string as True, so writing 'Successful' to stdOut should work
ET.SubElement(job1,"outputCheckScript").text = "grep 'Successful' "+os.path.join(workDir,checkOutput)
#The name of the campaign this job is associated with - can be either name or id
ET.SubElement(job1,"campaign").text = "Test"
#A list of expected input files - Job will not be submitted unless these exist
iF = ET.SubElement(job1,'inputFiles')
iF1 = ET.SubElement(iF,'elem')
#Mandatory fields for a file - name, fileDir
ET.SubElement(iF1,'name').text = 'testJob1In.data'
ET.SubElement(iF1,'fileDir').text = workDir
with open(os.path.join(workDir,'testJob1In.data')) as f:
	f.write("Test Job 1 Input")
#Can add as many of these as needed
iF2 = ET.SubElement(iF,'elem')
ET.SubElement(iF2,'name').text = 'testJob1Executable.data'
ET.SubElement(iF2,'fileDir').text = workDir
with open(os.path.join(workDir,'testJob1Executable.data')) as f:
	f.write("Test Job 1's Executable")
#A list of output files we expect to be created
#Job will not be marked successful until these exist
oF = ET.SubElement(job1,'outputFiles')
oF1 = ET.SubElement(oF,'elem')
ET.SubElement(oF1,'name').text = output
ET.SubElement(oF1,'fileDir').text = workDir

#Another test job in the same campaign that does the same thing...
workDir = "/lustre/atlas/scratch/danieltr/nph103"
output = 'testJob2.out'
checkOutput = 'testJob2Check.out'
job2 = ET.SubElement(data,"Job")
ET.SubElement(job2,"name").text = 'testJob2'
ET.SubElement(job2,"checkNodes").text = str(1)
ET.SubElement(job2,"nodes").text = str(1)
ET.SubElement(job2,"checkWallTime").text = '00:10:00'
ET.SubElement(job2,"wallTime").text = '00:10:00'
ET.SubElement(job2,"executionCommand").text = "serial echo 'testJob2 Successful' > "+os.path.join(workDir,output)
ET.SubElement(job2,"outputCheckCommand").text = "serial cp "+os.path.join(workDir,output)+" "+os.path.join(workDir,checkOutput)
ET.SubElement(job2,"outputCheckScript").text = "grep 'Successful' "+os.path.join(workDir,checkOutput)
ET.SubElement(job2,"campaign").text = "Test"
iF = ET.SubElement(job2,'inputFiles')
iF1 = ET.SubElement(iF,'elem')
ET.SubElement(iF1,'name').text = 'testJob2In.data'
ET.SubElement(iF1,'fileDir').text = workDir
with open(os.path.join(workDir,'testJob2In.data')) as f:
	f.write("Test Job 2 Input")
iF2 = ET.SubElement(iF,'elem')
ET.SubElement(iF2,'name').text = 'testJob2Executable.data'
ET.SubElement(iF2,'fileDir').text = workDir
with open(os.path.join(workDir,'testJob2Executable.data')) as f:
	f.write("Test Job 2's Executable")
oF = ET.SubElement(job2,'outputFiles')
oF1 = ET.SubElement(oF,'elem')
ET.SubElement(oF1,'name').text = output
ET.SubElement(oF1,'fileDir').text = workDir

#Write out the xml
tree = ET.ElementTree(data)
tree.write("exampleCampaign.xml")
