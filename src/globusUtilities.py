#!/usr/bin/env python

import json
import time
import sys
import os
import paramiko

from env.environment import globusUserName,localKeyFile

globusHost = "cli.globusonline.org"


def testActivation(endpoint, keyFile):
    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey.from_private_key_file(keyFile)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(globusHost, username=globusUserName, pkey=key)

    stdin, stdout, stderr = ssh.exec_command("endpoint-activate "+endpoint)

    err = stderr.readlines()
    if (len(err) > 0):
        print len(err)
        print err

    ssh.close()

def transferFile(fileName,destinationPath,destinationLocation,originPath,originLocation):
    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey.from_private_key_file(keyFile)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(globusHost, username=globusUserName, pkey=key)

    stdin, stdout, stderr = ssh.exec_command("endpoint-activate "+originLocation)

    err = stderr.readlines()
    if (len(err) > 0):
        print len(err)
        print err

    stdin, stdout, stderr = ssh.exec_command("endpoint-activate "+destinationLocation)

    err = stderr.readlines()
    if (len(err) > 0):
        print len(err)
        print err

    stdin, stdout, stderr = ssh.exec_command("transfer "originLocation+os.path.join(originPathPath,fileName)+" "+originLocation+os.path.join(originPathPath,fileName))

    ssh.close()
