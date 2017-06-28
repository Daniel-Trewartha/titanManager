# titanManager

To install:
Run setup.bash. This will create a virtualenv with the required packages to run the code.
Edit env/prodEnvironment.py appropriately
If you wish to run unit tests, also edit env/testEnvironment.py appropriately

To run:
submitXML takes in xml input.
Run using 'python submitXML.py Post/Patch/Delete yourXML.xml'
See examples folder for formatting of xmls.
Run jobManager.py to begin submitting
jobReports.py will provide a report of all campaigns/jobs/files currently in the database.

Running the example campaign:
Edit the workdir in examples/exampleCampaign.py appropriately
python exampleCampaign.py
python submitXML.py Post examples/exampleCampaign.py
python jobManager.py
The example campaign should submit a 2 node job, upon completion submit a 2 node check job, then report on its success.