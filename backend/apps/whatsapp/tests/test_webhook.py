from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class WebhookTest(TestCase):
    def test_webhook_received_message(self):
        payload = {
            'event': 'message.received',
            'session_id': 1,
            'timestamp': '2026-03-08T10:30:00Z',
            'data': {
                'from': '260971000000',
                'message': 'Hi there!',
                'type': 'text',
            }
        }

        response = self.client.post(
            reverse('whatsapp-webhook'),
            data=payload,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_webhook_missing_fields(self):
        response = self.client.post(
            reverse('whatsapp-webhook'),
            data={'event': 'message.received'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
