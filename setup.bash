#! /bin/bash

module load python
module load python_setuptools
module load python_virtualenv
virtualenv titanManager
source titanManager/bin/activate
pip install -r requirements.txt
#pip standard repos do not find faker for some reason
easy_install faker
easy_install globus_sdk