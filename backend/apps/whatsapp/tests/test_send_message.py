from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.users.models import User


class SendMessageTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    @patch('apps.whatsapp.views.MichoWAPIClient.send_text_message')
    def test_send_message_success(self, mock_send):
        mock_send.return_value = {
            'message_id': '3EB0A0B4F3',
            'status': 'sent',
            'to': '260971000000',
        }

        response = self.client.post(
            reverse('whatsapp-send'),
            data={'to': '260971000000', 'message': 'Hello'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'sent')
        self.assertEqual(response.data['to_number'], '260971000000')

    def test_send_message_unauthenticated(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            reverse('whatsapp-send'),
            data={'to': '260971000000', 'message': 'Hello'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
