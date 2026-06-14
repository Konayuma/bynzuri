from unittest.mock import patch
from django.test import TestCase
from apps.whatsapp.services import MichoWAPIClient, MichoWAPIError


class MichoWAPIClientTest(TestCase):
    def setUp(self):
        self.client = MichoWAPIClient()

    @patch('apps.whatsapp.services.requests.Session.post')
    def test_send_text_message_success(self, mock_post):
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            'data': {
                'message_id': '3EB0A0B4F3',
                'status': 'sent',
                'to': '260971000000',
                'created_at': '2026-03-08T10:30:00+00:00',
            }
        }

        result = self.client.send_text_message(to='260971000000', message='Hello')

        self.assertEqual(result['message_id'], '3EB0A0B4F3')
        self.assertEqual(result['status'], 'sent')

    @patch('apps.whatsapp.services.requests.Session.post')
    def test_send_text_message_failure(self, mock_post):
        mock_post.return_value.ok = False
        mock_post.return_value.json.return_value = {
            'error': {'message': 'WhatsApp session is not connected.'}
        }

        with self.assertRaises(MichoWAPIError):
            self.client.send_text_message(to='260971000000', message='Hello')
