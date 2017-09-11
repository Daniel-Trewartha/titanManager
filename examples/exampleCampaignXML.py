import xml.etree.ElementTree as ET
import os,subprocess

#Create a demonstration 'test' campaign with two jobs
workDir = os.environ['SCRATCH']
#Mandatory fields for a campaign - name
data = ET.Element("Data")
campaign = ET.SubElement(data,"Campaign")
#Campaign names are unique, should not contain white space
ET.SubElement(campaign,"name").text = 'Test'
#Campaign can have a wall time - if it does not infer one from the jobs
ET.SubElement(campaign,"wallTime").text = '00:10:00'
ET.SubElement(campaign,"checkWallTime").text = '00:10:00'
ET.SubElement(campaign,"workDir").text = workDir
#headers and footers for pbs submission scripts
header = ""
footer = ""
checkHeader = ""
checkFooter = ""
ET.SubElement(campaign,"header").text = header
ET.SubElement(campaign,"footer").text = footer
ET.SubElement(campaign,"checkHeader").text = checkHeader
ET.SubElement(campaign,"checkFooter").text = checkFooter

#Create a job
#Mandatory fields for a job - name, campaign
output = 'testJob1.out'
checkOutput = 'testJob1Check.out'
outputExec = 'testJob.bash'
checkOutputExec = 'checkTestJob.bash'
job1 = ET.SubElement(data,"Job")
#Create executables to run the job and check it
with open(os.path.join(workDir,outputExec),'w') as f:
	f.write("#! /bin/bash \n")
	f.write("echo $1 > $2")
with open(os.path.join(workDir,checkOutputExec),'w') as f:
	f.write("#! /bin/bash \n")
	f.write("cp $1 $2")
os.system("chmod +x "+os.path.join(workDir,outputExec))
os.system("chmod +x "+os.path.join(workDir,checkOutputExec))

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
#Also note arguments to executable fed in as usual with serial
ET.SubElement(job1,"executionCommand").text = os.path.join(workDir,outputExec)+" 'Successful!' "+os.path.join(workDir,output)
#Check command to be executed with wraprun
#test Job's check copies the contents of the output file verbatim
ET.SubElement(job1,"checkOutputCommand").text = os.path.join(workDir,checkOutputExec)+" "+os.path.join(workDir,output)+" "+os.path.join(workDir,checkOutput)
#Front end script to verify the output of checker
#Should write True or False to stdout
#test Job greps 'Successful' in the expected check output location
#Python evaluates any non-empty string as True, so writing 'Successful' to stdOut should work
ET.SubElement(job1,"checkOutputScript").text = "grep 'Successful' "+os.path.join(workDir,checkOutput)
#The name of the campaign this job is associated with - can be either name or id
ET.SubElement(job1,"campaign").text = "Test"
#A list of expected input files - Job will not be submitted unless these exist
iF = ET.SubElement(job1,'inputFiles')
iF1 = ET.SubElement(iF,'elem')
#Mandatory fields for a file - name, fileDir
ET.SubElement(iF1,'name').text = outputExec
ET.SubElement(iF1,'fileDir').text = workDir
#Can add as many of these as needed
iF2 = ET.SubElement(iF,'elem')
ET.SubElement(iF2,'name').text = checkOutputExec
ET.SubElement(iF2,'fileDir').text = workDir
#A list of output files we expect to be created
#Job will not be marked successful until these exist
oF = ET.SubElement(job1,'outputFiles')
oF1 = ET.SubElement(oF,'elem')
ET.SubElement(oF1,'name').text = output
ET.SubElement(oF1,'fileDir').text = workDir

#Another test job in the same campaign that does the same thing...
output = 'testJob2.out'
checkOutput = 'testJob2Check.out'
job2 = ET.SubElement(data,"Job")
ET.SubElement(job2,"name").text = 'testJob2'
ET.SubElement(job2,"checkNodes").text = str(1)
ET.SubElement(job2,"nodes").text = str(1)
ET.SubElement(job2,"checkWallTime").text = '00:10:00'
ET.SubElement(job2,"wallTime").text = '00:10:00'
ET.SubElement(job2,"executionCommand").text = os.path.join(workDir,outputExec)+" 'Successful!' "+os.path.join(workDir,output)
#Check command to be executed with wraprun
#test Job's check copies the contents of the output file verbatim
ET.SubElement(job2,"checkOutputCommand").text = os.path.join(workDir,checkOutputExec)+" "+os.path.join(workDir,output)+" "+os.path.join(workDir,checkOutput)
ET.SubElement(job2,"checkOutputScript").text = "grep 'Successful' "+os.path.join(workDir,checkOutput)
ET.SubElement(job2,"campaign").text = "Test"
iF = ET.SubElement(job2,'inputFiles')
iF1 = ET.SubElement(iF,'elem')
ET.SubElement(iF1,'name').text = outputExec
ET.SubElement(iF1,'fileDir').text = workDir
iF2 = ET.SubElement(iF,'elem')
ET.SubElement(iF2,'name').text = checkOutputExec
ET.SubElement(iF2,'fileDir').text = workDir
oF = ET.SubElement(job2,'outputFiles')
oF1 = ET.SubElement(oF,'elem')
ET.SubElement(oF1,'name').text = output
ET.SubElement(oF1,'fileDir').text = workDir

#Write out the xml
tree = ET.ElementTree(data)
tree.write("exampleCampaign.xml")
