import time
import os
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
CREDENTIAL = None
CREDENTIAL_WAIT = False


def AccountToken(scope):
    return GetCredential().get_token(scope)

def GetCredential():
    global CREDENTIAL_WAIT, CREDENTIAL
    if CREDENTIAL != None:
        return CREDENTIAL
    elif CREDENTIAL_WAIT:
        while CREDENTIAL == None:
            time.sleep(0.1)
        return GetCredential()
    else:
        CREDENTIAL_WAIT = True
        if(os.environ.get("MSI_SECRET")):
            CREDENTIAL = DefaultAzureCredential(additionally_allowed_tenants = ["*"])
        else:
            CREDENTIAL = InteractiveBrowserCredential(additionally_allowed_tenants = ["*"])
        return CREDENTIAL