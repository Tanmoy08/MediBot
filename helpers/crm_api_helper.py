import adal
import requests
import json

class CrmApiHelper:
    CLIENT_ID = '854368a7-ccec-418b-b401-2b5558aa8b1d'
    RESOURCE_URI = ' https://orgde91d4a0.crm.dynamics.com'
    AUTHORITY_URI = 'https://login.microsoftonline.com/296656d2-6ffe-41ce-b33e-c782de9a6b6e'
    CLIENT_SECRET = 'Q5U62.1Fh._oC1YX10.JI1qP9Qs40-AR4X'

    async def get_result(self, api: str):
        context = adal.AuthenticationContext(CrmApiHelper.AUTHORITY_URI, api_version=None)
        token = context.acquire_token_with_client_credentials(CrmApiHelper.RESOURCE_URI, CrmApiHelper.CLIENT_ID, CrmApiHelper.CLIENT_SECRET)

        requestheader = {
                'Authorization': 'Bearer ' + token["accessToken"],
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
        response = requests.get(api, headers = requestheader)
        return response

    async def Create_Record(self, api: str, data):
        context = adal.AuthenticationContext(CrmApiHelper.AUTHORITY_URI, api_version=None)
        token = context.acquire_token_with_client_credentials(CrmApiHelper.RESOURCE_URI, CrmApiHelper.CLIENT_ID, CrmApiHelper.CLIENT_SECRET)

        requestheader = {
                'Authorization': 'Bearer ' + token["accessToken"],
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
        response = requests.post(api, headers = requestheader, data = json.dumps(data))
        return response
