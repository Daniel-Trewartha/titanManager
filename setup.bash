#! /bin/bash

echo Enter Cluster Name

read clusterName

setupScript=$(python env/setup.py ${clusterName}Adaptor)

bash ${setupScript}