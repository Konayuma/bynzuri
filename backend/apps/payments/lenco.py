import hashlib
import hmac
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

LENCO_API_BASE = 'https://api.lenco.co/access/v2'


class LencoService:
    def __init__(self):
        self.api_key = settings.LENCO_API_KEY
        self.webhook_secret = settings.LENCO_WEBHOOK_SECRET
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def initiate_collection(self, amount: float, reference: str, phone: str, operator: str, country: str = 'zm') -> dict:
        payload = {
            'amount': amount,
            'reference': reference,
            'phone': phone,
            'operator': operator,
            'country': country,
            'bearer': 'merchant',
        }

        try:
            response = requests.post(
                f'{LENCO_API_BASE}/collections/mobile-money',
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'Lenco collection failed: {e}')
            return {'status': False, 'message': str(e)}

    def get_collection_status(self, reference: str) -> dict:
        try:
            response = requests.get(
                f'{LENCO_API_BASE}/collections/status/{reference}',
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'Lenco status check failed: {e}')
            return {'status': False, 'message': str(e)}

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        webhook_hash_key = hashlib.sha256(self.api_key.encode()).hexdigest()
        expected = hmac.new(
            webhook_hash_key.encode(),
            payload,
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


lenco_service = LencoService()
