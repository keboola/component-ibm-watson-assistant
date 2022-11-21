import logging
import json
from typing import Dict, Tuple
from ibm_watson_assistant import WatsonAssistantClient, ClientApiException
import time

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException
from ibm_cloud_sdk_core.api_exception import ApiException

KEY_WORKSPACE_ID = "workspace_id"
KEY_API_KEY = "#api_key"
KEY_MODE = "mode"
KEY_LIST_LOGS_FILTER = "list_logs_filter"
KEY_LOG_FILE_NAME = "list_logs_file_name"
KEY_WATSON_VERSION = "version"
KEY_WAIT = "wait"

REQUIRED_PARAMETERS = [KEY_API_KEY, KEY_WATSON_VERSION]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    def __init__(self):
        super().__init__(required_parameters=REQUIRED_PARAMETERS,
                         required_image_parameters=REQUIRED_IMAGE_PARS)
        self.remaining_limit = 0
        params = self.configuration.parameters
        watson_version = params.get(KEY_WATSON_VERSION)
        api_key = params.get(KEY_API_KEY)
        self.wait = params.get(KEY_WAIT)

        self.watson_client = WatsonAssistantClient(api_key, watson_version)
        self.watson_client.login()

    def run(self) -> None:
        params = self.configuration.parameters
        mode = params.get(KEY_MODE, "workspace")
        workspace_id = params.get(KEY_WORKSPACE_ID)
        if self.wait:
            logging.info("Wait mode is set to true. In case APIRateLimit is reached the component will wait"
                         " for ApiRateLimit refresh and then continue.")

        if mode == "workspace":
            self.get_and_write_workspaces(workspace_id)
        elif mode == "list_all_logs":
            list_logs_filter = params.get(KEY_LIST_LOGS_FILTER, "")
            list_logs_file_name = params.get(KEY_LOG_FILE_NAME, "logs.json")
            self.get_and_save_all_logs(list_logs_filter, list_logs_file_name)
        else:
            raise UserException(f"Mode {mode} is not a valid mode. Use either 'workspace' or 'list_all_logs'")

    def get_workspace_data(self, workspace_id: str):
        try:
            return self.watson_client.get_workspace(workspace_id)
        except ClientApiException as client_exc:
            raise UserException(client_exc) from client_exc

    def get_and_save_all_logs(self, list_logs_filter: str, list_logs_file_name: str) -> None:
        out_file = self.create_out_file_definition(list_logs_file_name, tags=["ibm_watson_assistant", "logs"])
        last_page = False
        first_page = True
        cursor = None
        # each page is written individually so there is no memory leak,
        # therefore the file needs to start with {"logs" :[
        # then the logs are written in, then the file needs to be finished by adding ])
        self.prep_json_file(out_file)
        while not last_page:
            logs_response = self.get_all_logs(list_logs_filter, cursor=cursor)
            logs = logs_response.get("logs")
            self.write_logs_to_file(out_file, logs, first_page)
            cursor = logs_response.get("pagination", {}).get("next_cursor")
            if not cursor:
                last_page = True
            first_page = False

        self.finish_json_file(out_file)
        self.write_manifest(out_file)

    @staticmethod
    def prep_json_file(out_file):
        with open(out_file.full_path, 'a') as fp:
            fp.write('{"logs":[')

    @staticmethod
    def finish_json_file(out_file):
        with open(out_file.full_path, 'a') as fp:
            fp.write(']}')

    @staticmethod
    def write_logs_to_file(out_file, logs, first_page):
        with open(out_file.full_path, 'a') as fp:
            for log in logs:
                if not first_page:
                    fp.write(",")
                else:
                    first_page = False
                json.dump(log, fp)

    @staticmethod
    def wait_if_limit_reached(headers) -> None:
        """
        Checks for X-RateLimit-Remaining and X-RateLimit-Reset in response headers and waits until
        X-RateLimit-Reset is reached.
        """
        if int(headers.get("X-RateLimit-Remaining")) == 0:
            now = time.time()
            wait_until = int(headers.get("X-RateLimit-Reset"))
            logging.info(f"Api limit reached, will sleep for {int(wait_until - now)} seconds and then continue.")
            while time.time() <= wait_until:
                time.sleep(5)
        return

    @staticmethod
    def get_remaining_limit(r):
        try:
            return int(r.headers.get("X-RateLimit-Remaining"))
        except AttributeError:
            return 0

    def fetch_logs(self, filters, cursor) -> Tuple[Dict, Dict]:
        r = self.watson_client.get_all_logs(filters, cursor=cursor)
        limit = self.get_remaining_limit(r)
        if limit > 0:
            try:
                headers = r.headers
                result = r.get_result()
            except AttributeError:
                self.wait_if_limit_reached(headers)
                result, headers = self.fetch_logs(filters, cursor)
            headers = r.headers
            return result, headers
        else:
            # Encountered state when limit has been reached when component has started.
            logging.info("Cannot fetch logs and remaining API RateLimit reset time probably due to "
                         "reaching API RateLimit. The component will now sleep for a minute and try again.")
            time.sleep(60)
            result, headers = self.fetch_logs(filters, cursor)
            return result, headers

    def fetch_logs_with_wait(self, filters, cursor) -> Tuple[Dict, Dict]:
        r = self.watson_client.get_all_logs(filters, cursor=cursor)
        headers = r.headers
        result = r.get_result()
        return result, headers

    def get_all_logs(self, filters: str, cursor: str = None) -> Dict:
        try:
            if self.wait:
                result, headers = self.fetch_logs_with_wait(filters, cursor)
            else:
                result, headers = self.fetch_logs(filters, cursor)
                logging.info(f"Remaining rate-limit: {int(headers.get('X-RateLimit-Remaining'))}")
            return result
        except ClientApiException as client_exc:
            raise UserException(f"{client_exc}. Check the validity of your API token, your version, and "
                                f"make sure your filters are setup correctly") from client_exc

    def get_and_write_workspaces(self, workspace_id):
        workspace_data = self.get_workspace_data(workspace_id)

        file_name = f"{workspace_id}_workspace.json"
        out_file = self.create_out_file_definition(file_name, tags=[workspace_id, "ibm_watson_assistant", "workspaces"])

        with open(out_file.full_path, 'w') as fp:
            json.dump(workspace_data, fp)
        self.write_manifest(out_file)


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
