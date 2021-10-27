import logging
import json
from ibm_watson_assistant import WatsonAssistantClient, ClientApiException

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

REQUIRED_PARAMETERS = []
REQUIRED_IMAGE_PARS = []

KEY_WORKSPACE_ID = "workspace_id"
KEY_API_KEY = "#api_key"
KEY_WATSON_VERSION = "version"


class Component(ComponentBase):
    def __init__(self):
        super().__init__(required_parameters=REQUIRED_PARAMETERS,
                         required_image_parameters=REQUIRED_IMAGE_PARS)
        params = self.configuration.parameters
        watson_version = params.get(KEY_WATSON_VERSION)
        api_key = params.get(KEY_API_KEY)

        self.watson_client = WatsonAssistantClient(api_key, watson_version)
        self.watson_client.login()

    def run(self):
        params = self.configuration.parameters
        workspace_id = params.get(KEY_WORKSPACE_ID)
        workspace_data = self.get_workspace_data(workspace_id)

        file_name = f"{workspace_id}_workspace.json"
        out_file = self.create_out_file_definition(file_name, tags=[workspace_id, "ibm_watson_assistant"])

        with open(out_file.full_path, 'w') as fp:
            json.dump(workspace_data, fp)
        self.write_manifest(out_file)

    def get_workspace_data(self, workspace_id):
        try:
            return self.watson_client.get_workspace(workspace_id)
        except ClientApiException as client_exc:
            raise UserException(client_exc) from client_exc


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
