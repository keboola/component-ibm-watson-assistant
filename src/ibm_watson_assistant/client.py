from retry import retry
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
import logging

WATSON_ENDPOINT = 'https://api.eu-de.assistant.watson.cloud.ibm.com/'


class ClientApiException(Exception):
    pass


class WatsonAssistantClient:
    def __init__(self, api_key, watson_version):
        self.api_key = api_key
        self.watson_version = watson_version
        self.skill = None
        self.client = None

    def login(self):
        self.client = AssistantV1(version=self.watson_version, authenticator=IAMAuthenticator(self.api_key))
        self.client.set_service_url(WATSON_ENDPOINT)

    @retry(tries=5)
    def get_workspace(self, workspace_id):
        try:
            response = self.client.get_workspace(workspace_id=workspace_id, export=True).get_result()
        except ApiException as api_exc:
            raise ClientApiException(api_exc) from api_exc
        return response

    @retry(tries=5)
    def get_all_logs(self, filters, cursor=None):
        try:
            return self.client.list_all_logs(filter=filters, cursor=cursor)
        except ApiException as api_exc:
            logging.warning(f"ApiException: {api_exc}")
            # raise ClientApiException(api_exc) from api_exc
