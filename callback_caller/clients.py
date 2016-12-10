import requests
from django.conf import settings
from twilio.rest import TwilioRestClient


class RestClient(object):
    def create_call(self, **kwargs):
        raise NotImplementedError


class RestClientTwilio(RestClient):
    def __init__(self):
        super().__init__()
        self.client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def create_call(self, **kwargs):
        return self.client.calls.create(
            kwargs['client_phone'],
            settings.TWILIO_DEFAULT_FROM,
            kwargs['url'],
            status_method='GET',
            status_callback=kwargs['status_callback'],
            method='GET',
            timeout=settings.CALLBACK_CLIENT_CALL_TIMEOUT
        )


class RestClientVoximplant(RestClient):
    def create_call(self, **kwargs):
        requests.get('https://api.voximplant.com/platform_api/StartScenarios/',
                     params={
                         'account_id': settings.VOXIMPLANT_ACCOUNT_ID,
                         'api_key': settings.VOXIMPLANT_API_KEY,
                         'rule_id': settings.VOXIMPLANT_RULE_ID,
                         'script_custom_data': "|".join(
                             (kwargs['client_phone'],
                              settings.TWILIO_DEFAULT_FROM,
                              kwargs['url'],
                              kwargs['status_callback'],
                              str(settings.CALLBACK_CLIENT_CALL_TIMEOUT))
                         )
                     })
