#!/usr/bin/env python

import json
import time
import sys
import webbrowser
from env.environment import globusRefreshTokens

from globus_sdk import NativeAppAuthClient, TransferClient, RefreshTokenAuthorizer
from globus_sdk.exc import GlobusAPIError

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

def doNativeAppAuthentication(client_id,requested_scopes=None):
    """
    Does a Native App authentication flow and returns a
    dict of tokens keyed by service name.
    """
    client = NativeAppAuthClient(client_id=client_id)
    # pass refresh_tokens=True to request refresh tokens
    client.oauth2_start_flow(requested_scopes=scope,
                             redirect_uri='https://auth.globus.org/v2/web/auth-code',
                             refresh_tokens=True)

    url = client.oauth2_get_authorize_url()

    print('Please visit the url at \n{}'.format(url))

    auth_code = input('Enter the auth code provided: ').strip()

    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    # return a set of tokens, organized by resource server name
    return token_response.by_resource_server

def acquireRefreshTokens():
    #Establish access tokens, set up authorizer and transfer clients
    tokens = None
    try:
        tokens = loadTokensFromFile(globusRefreshTokens)
    except:
        pass

    if not tokens:
        tokens = doNativeAppAuthentication(clientID, scope)
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

    auth_client = NativeAppAuthClient(client_id=clientID)

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
        transfer.endpoint_autoactivate(originLocation)
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
    transferData.add_item(os.path.join(originPath,filename),os.path.join(destinationPath,filename))
    transferClient.submit_transfer(transferData)
