import adal
import requests
import json

class CrmApiHelper:
    CLIENT_ID = '928a59a1-2506-4319-9c7e-be54d4ed6348'
    RESOURCE_URI = 'https://oneviewdev.crm.dynamics.com'
    AUTHORITY_URI = 'https://login.microsoftonline.com/e85feadf-11e7-47bb-a160-43b98dcc96f1'
    CLIENT_SECRET = '_5inX-I1Uq3O..kSRY45S6moF_e9J5qW5H'

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

    async def write_text_date_field(self, api: str, data):
        context = adal.AuthenticationContext(CrmApiHelper.AUTHORITY_URI, api_version=None)
        token = context.acquire_token_with_client_credentials(CrmApiHelper.RESOURCE_URI, CrmApiHelper.CLIENT_ID, CrmApiHelper.CLIENT_SECRET)

        requestheader = {
                'Authorization': 'Bearer ' + token["accessToken"],
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
        response = requests.put(api, headers = requestheader, data = json.dumps(data))
        return response
