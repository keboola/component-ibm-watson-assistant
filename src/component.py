import logging
from os import path
import json
from ibm_watson_assistant import WatsonAssistantClient

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

REQUIRED_PARAMETERS = []
REQUIRED_IMAGE_PARS = []

KEY_S3_BUCKET = "s3_bucket"
KEY_CLOUD_STORAGE_API_KEY = "#cloud_storage_api_key"
KEY_ASSISTANT_API_KEY = "#assistant_api_key"
KEY_IAM_AUTHENTICATOR = "iam_authenticator"
KEY_WATSON_VERSION = "version"
KEY_S3_SKILL_OBJECT = "s3_skill_object"


class Component(ComponentBase):
    def __init__(self):
        super().__init__(required_parameters=REQUIRED_PARAMETERS,
                         required_image_parameters=REQUIRED_IMAGE_PARS)
        params = self.configuration.parameters
        s3_bucket = params.get(KEY_S3_BUCKET)
        cloud_storage_api_key = params.get(KEY_CLOUD_STORAGE_API_KEY)
        assistant_api_key = params.get(KEY_ASSISTANT_API_KEY)
        watson_version = params.get(KEY_WATSON_VERSION)
        s3_skill_object = params.get(KEY_S3_SKILL_OBJECT)

        self.watson_client = WatsonAssistantClient(s3_bucket,
                                                   cloud_storage_api_key,
                                                   assistant_api_key,
                                                   watson_version,
                                                   s3_skill_object)
        self.watson_client.login()

    def run(self):
        # params = self.configuration.parameters
        workspace = self.watson_client.get_skill()
        workspace_data = self.watson_client.get_workspace(workspace)
        output = path.join(self.files_out_path, "workspace.json")
        with open(output, 'w') as fp:
            json.dump(workspace_data, fp)


if __name__ == "__main__":
    try:
        comp = Component()
        comp.run()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
