import hashlib
import hmac
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class LencoService:
    @property
    def configured(self):
        return bool(settings.LENCO_API_KEY)

    def _request(self, method, path, **kwargs):
        if not self.configured:
            return {'status': False, 'configuration_error': True}
        try:
            response = requests.request(
                method, f'{settings.LENCO_API_BASE_URL.rstrip("/")}{path}',
                headers={'Authorization': f'Bearer {settings.LENCO_API_KEY}', 'Content-Type': 'application/json'},
                timeout=15, **kwargs,
            )
            if response.status_code >= 500:
                return {'status': False, 'uncertain': True}
            if not response.ok:
                try:
                    error_code = str(response.json().get('errorCode', ''))
                except (ValueError, AttributeError):
                    error_code = ''
                # Authentication failures and documented validation errors cannot start a collection.
                rejected = response.status_code in (401, 403) or error_code in ('01', '12')
                logger.warning('Lenco request returned HTTP %s (code %s)', response.status_code, error_code or 'unknown')
                return {'status': False, 'rejected': rejected, 'uncertain': not rejected}
            result = response.json()
            return result if isinstance(result, dict) else {'status': False, 'uncertain': True}
        except (requests.RequestException, ValueError):
            logger.warning('Lenco request could not be completed', exc_info=True)
            return {'status': False, 'uncertain': True}

    def initiate_collection(self, amount, reference, phone, operator):
        return self._request('POST', '/collections/mobile-money', json={
            'amount': float(amount), 'reference': reference, 'phone': phone,
            'operator': operator, 'country': 'zm', 'bearer': 'merchant',
        })

    def get_collection_status(self, reference):
        return self._request('GET', f'/collections/status/{reference}')

    def verify_webhook_signature(self, payload, signature):
        if not self.configured or not signature:
            return False
        key = hashlib.sha256(settings.LENCO_API_KEY.encode()).hexdigest()
        expected = hmac.new(key.encode(), payload, hashlib.sha512).hexdigest()
        return hmac.compare_digest(expected, signature)


lenco_service = LencoService()
