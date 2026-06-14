import logging
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


class MichoWAPIError(Exception):
    pass


class MichoWAPIClient:
    BASE_URL = 'https://wapi.michotech.me/api/v1'

    def __init__(self):
        self.api_key = settings.MICHOWAPI_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        })

    def send_text_message(self, to: str, message: str) -> dict:
        response = self.session.post(
            f'{self.BASE_URL}/messages/text',
            json={'to': to, 'message': message},
        )

        if not response.ok:
            logger.error(
                'MichoWAPI send_text failed: %s %s',
                response.status_code, response.text,
            )
            raise MichoWAPIError(response.json().get('error', {}).get('message', 'Unknown error'))

        return response.json()['data']

    def get_message_history(self, params: dict | None = None) -> dict:
        response = self.session.get(
            f'{self.BASE_URL}/messages',
            params=params or {},
        )

        if not response.ok:
            logger.error(
                'MichoWAPI get_history failed: %s %s',
                response.status_code, response.text,
            )
            raise MichoWAPIError(response.json().get('error', {}).get('message', 'Unknown error'))

        return response.json()

    def get_message(self, message_id: str) -> dict:
        response = self.session.get(f'{self.BASE_URL}/messages/{message_id}')

        if not response.ok:
            logger.error(
                'MichoWAPI get_message failed: %s %s',
                response.status_code, response.text,
            )
            raise MichoWAPIError(response.json().get('error', {}).get('message', 'Unknown error'))

        return response.json()
