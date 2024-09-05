from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
import logging
import time
import functools

WATSON_ENDPOINT = 'https://api.eu-de.assistant.watson.cloud.ibm.com/'


class ClientApiException(Exception):
    pass


def retry_on_rate_limit(func):
    """Decorator to handle retry logic on rate limit."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        retries = 0
        while retries < self.max_retries:
            try:
                return func(self, *args, **kwargs)
            except ApiException as e:
                retries += 1
                retry_after = self.get_retry_after(e.http_response.headers._store)
                logging.info(
                    f"Rate limit reached. Attempt {retries} of {self.max_retries}. Sleeping for {retry_after} seconds")
                time.sleep(retry_after)
        raise ClientApiException(f"Failed to complete {func.__name__} after {self.max_retries} attempts.")

    return wrapper


class WatsonAssistantClient:
    def __init__(self, api_key, watson_version, max_retries=3):
        self.api_key = api_key
        self.watson_version = watson_version
        self.skill = None
        self.client = None
        self.retry_after = 60
        self.max_retries = max_retries

    def login(self):
        """Authenticate and initialize the Watson Assistant client."""
        authenticator = IAMAuthenticator(self.api_key)
        self.client = AssistantV1(version=self.watson_version, authenticator=authenticator)
        self.client.set_service_url(WATSON_ENDPOINT)

    @retry_on_rate_limit
    def get_workspace(self, workspace_id):
        return self.client.get_workspace(workspace_id=workspace_id, export=True).get_result()

    @retry_on_rate_limit
    def get_all_logs(self, filters, cursor=None):
        return self.client.list_all_logs(filter=filters, cursor=cursor)

    def fetch_logs(self, filters, cursor) -> (dict, dict):
        r = self.get_all_logs(filters, cursor=cursor)
        headers = r.headers
        return r.get_result(), headers

    @staticmethod
    def get_retry_after(headers: dict) -> float:
        ratelimit_reset = headers.get("x-ratelimit-reset")[1]
        if not ratelimit_reset:
            ratelimit_reset = headers.get("X-RateLimit-Reset")

        if not ratelimit_reset:
            raise ClientApiException("Unretryable error: No rate limit reset header found")

        sleep_for = float(ratelimit_reset) - time.time()
        logging.info(f"Rate limit reached. Sleeping for {sleep_for} seconds")
        return sleep_for
