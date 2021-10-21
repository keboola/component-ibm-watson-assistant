import io
import ibm_boto3
import pandas as pd
from ibm_watson import AssistantV1
from botocore.client import Config
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

IBM_AUTH_ENDPOINT = 'https://iam.eu-de.bluemix.net/oidc/token'
S3_ENDPOINT_URL = 'https://s3.eu.cloud-object-storage.appdomain.cloud'
WATSON_ENDPOINT = 'https://api.eu-de.assistant.watson.cloud.ibm.com/'


class WatsonAssistantClient:
    def __init__(self, s3_bucket, cloud_storage_api_key, assistant_api_key, watson_version, s3_skill_object,
                 service_name="s3"):
        self.s3_bucket = s3_bucket
        self.cloud_storage_api_key = cloud_storage_api_key
        self.assistant_api_key = assistant_api_key
        self.watson_version = watson_version
        self.service_name = service_name
        self.s3_skill_object = s3_skill_object
        self.skill = None
        self.cloud_client = None
        self.assistant_client = None

    def login(self):
        self._cloud_client_login()
        self._assistant_client_login()

    def _cloud_client_login(self):
        self.cloud_client = ibm_boto3.client(service_name=self.service_name,
                                             ibm_api_key_id=self.cloud_storage_api_key,
                                             ibm_auth_endpoint=IBM_AUTH_ENDPOINT,
                                             config=Config(signature_version='oauth'),
                                             endpoint_url=S3_ENDPOINT_URL)

    def _assistant_client_login(self):
        self.assistant_client = AssistantV1(version=self.watson_version,
                                            authenticator=IAMAuthenticator(self.assistant_api_key)
                                            )
        self.assistant_client.set_service_url(WATSON_ENDPOINT)

    def get_skill(self):
        body = self.cloud_client.get_object(Bucket=self.s3_bucket,
                                            Key='skills_setup_intern_chitchat.xlsx')['Body']
        WA_skills = pd.read_excel(io.BytesIO(body.read()))
        skill_ID = WA_skills.iloc[0, 1]
        return skill_ID

    def get_workspace(self, workspace_id):
        response = self.assistant_client.get_workspace(workspace_id=workspace_id, export=True).get_result()
        return response

    def list_intents(self, workspace_id):
        response = self.assistant_client.list_intents(workspace_id=workspace_id, page_limit=2, export=True).get_result()
        return response

    # def list_workspaces(self):
    #     response = self.assistant_client.list_workspaces().get_result()
    #     pass
    #
    # def list_examples(self, workspace_id, intent):
    #     response = self.assistant_client.list_examples(workspace_id, intent).get_result()
    #     pass
    #
    # def list_counterexamples(self, workspace_id):
    #     """
    #     List the counterexamples for a workspace. Counterexamples are examples that have
    #     been marked as irrelevant input.
    #     """
    #     response = self.assistant_client.list_counterexamples(workspace_id).get_result()
    #     pass
    #
    # def list_entities(self, workspace_id):
    #     response = self.assistant_client.list_entities(workspace_id, export=True).get_result()
    #     pass
    #
    # def list_dialog_nodes(self, workspace_id):
    #     response = self.assistant_client.list_dialog_nodes(workspace_id).get_result()
    #     pass
