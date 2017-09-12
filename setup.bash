#! /bin/bash

module load python
conda create -n titanManager --file requirements.txt
source activate titanManager
