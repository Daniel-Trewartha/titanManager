#! /bin/bash

module load python
conda create -n titanManager
source activate titanManager
conda install --file requirements.txt
#pip standard repos do not find faker for some reason
