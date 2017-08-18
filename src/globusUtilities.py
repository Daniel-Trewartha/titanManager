#!/usr/bin/env python

import json
import time
import sys
import os
from env.environment import globusRefreshTokens
from env.globusSecret import secret

from globus_sdk import ConfidentialAppAuthClient, TransferClient, RefreshTokenAuthorizer
from globus_sdk.exc import GlobusAPIError
import globus_sdk

clientID = "3fedb375-4458-42d7-b17c-7f5d4be1ceac"
scope = ('urn:globus:auth:scope:transfer.api.globus.org:all')

def loadTokensFromFile(filepath):
    """Load a set of saved tokens."""
    with open(filepath, 'r') as f:
        tokens = json.load(f)

    return tokens

def saveTokensToFile(filepath, tokens):
    """Save a set of tokens for later use."""
    with open(filepath, 'w') as f:
        json.dump(tokens, f)

def updateTokensFileOnRefresh(token_response):
    """
    Authorizer requires a refresh function that has only tokens as input.
    So wrap the save file function.
    """
    saveTokensToFile(globusRefreshTokens, token_response.by_resource_server)


def doClientCredentialsAppAuthentication(client_id, client_secret):
    """
    Does a client credential grant authentication and returns a
    dict of tokens keyed by service name.
    """
    client = globus_sdk.ConfidentialAppAuthClient(
            client_id=client_id,
            client_secret=client_secret)
    token_response = client.oauth2_client_credentials_tokens()

    return token_response.by_resource_server


def getConfidentialAppAuthorizer(client_id, client_secret):
    tokens = doClientCredentialsAppAuthentication(
            client_id=client_id,
            client_secret=client_secret)
    transfer_tokens = tokens['transfer.api.globus.org']
    transfer_access_token = transfer_tokens['access_token']

    return globus_sdk.AccessTokenAuthorizer(transfer_access_token)


def acquireRefreshTokens():
    #Establish access tokens, set up authorizer and transfer clients
    tokens = None
    try:
        tokens = loadTokensFromFile(globusRefreshTokens)
    except:
        pass

    if not tokens:
        tokens = doClientCredentialsAppAuthentication(clientID, client_secret)
        try:
            saveTokensToFile(globusRefreshTokens, tokens)
        except:
            print("Unable to acquire globus tokens. Remote files will not be transferred.")

def establishTransferClient():
    #Establish access tokens, set up authorizer and transfer clients
    tokens = None
    try:
        tokens = loadTokensFromFile(globusRefreshTokens)
    except:
        print("Unable to connect to globus. Remote files will not be transferred.")
        raise GlobusAPIError


    transferTokens = tokens['transfer.api.globus.org']

    auth_client = getConfidentialAppAuthorizer(client_id=clientID,client_secret=secret)

    authorizer = RefreshTokenAuthorizer(
        transferTokens['refresh_token'],
        auth_client,
        access_token=transferTokens['access_token'],
        expires_at=transferTokens['expires_at_seconds'],
        on_refresh=updateTokensFileOnRefresh)

    transfer = TransferClient(authorizer=authorizer)

    return transfer 

def transfer_file(fileName,destinationPath,destinationLocation,originPath,originLocation):
    transferClient = establishTransferClient()
    try:
        transferClient.endpoint_autoactivate(originLocation)
    except GlobusAPIError as ex:
        print(ex)
        if ex.http_status == 401:
            sys.exit('Refresh token has expired. '
                     'Please delete refresh-tokens.json and try again.')
        else:
            raise ex

    transferData = globus_sdk.TransferData(transferClient, originLocation,
                                 destinationLocation,
                                 sync_level="checksum")
    transferData.add_item(os.path.join(originPath,fileName),os.path.join(destinationPath,fileName))
    transferClient.submit_transfer(transferData)
