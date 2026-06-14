from unittest.mock import patch, ANY
from decimal import Decimal
from django.test import TestCase
from apps.categories.models import Category
from apps.products.models import Product
from apps.delivery.models import Province, Town, DeliveryMethod
from apps.whatsapp.models import Conversation, WhatsAppMessage
from apps.whatsapp.bot import process_message


class BotFlowTest(TestCase):
    def setUp(self):
        self.phone = '260971000000'
        self.cat = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            category=self.cat, title='Phone', slug='phone',
            description='A great phone', price=Decimal('1500.00'), stock=10,
            is_active=True,
        )
        self.product2 = Product.objects.create(
            category=self.cat, title='Charger', slug='charger',
            description='Fast charger', price=Decimal('100.00'), stock=20,
            is_active=True,
        )
        self.province = Province.objects.create(name='Lusaka', slug='lusaka')
        self.town = Town.objects.create(province=self.province, name='Lusaka', slug='lusaka')
        self.delivery = DeliveryMethod.objects.create(
            name='Courier', description='Fast', price=Decimal('35.00'),
            estimated_days='1-2 days', is_active=True,
        )

    def _patch_send(self):
        patcher = patch('apps.whatsapp.bot.MichoWAPIClient.send_text_message')
        mock_send = patcher.start()
        mock_send.return_value = {'message_id': 'mock123', 'status': 'sent'}
        self.addCleanup(patcher.stop)
        # Patch Celery task to avoid needing a running broker
        celery_patcher = patch('apps.whatsapp.tasks.send_whatsapp_notification.delay')
        mock_celery = celery_patcher.start()
        mock_celery.return_value = None
        self.addCleanup(celery_patcher.stop)
        return mock_send

    def test_main_menu_starts_conversation(self):
        mock_send = self._patch_send()
        process_message(self.phone, '1')

        conv = Conversation.objects.get(phone_number=self.phone)
        self.assertEqual(conv.state, 'browsing_categories')

        sent = mock_send.call_args[1]['message']
        self.assertIn('Electronics', sent)

    def test_browse_products_in_category(self):
        mock_send = self._patch_send()
        process_message(self.phone, '1')
        mock_send.reset_mock()

        process_message(self.phone, '1')

        sent = mock_send.call_args[1]['message']
        self.assertIn('Phone', sent)
        self.assertIn('Charger', sent)

        conv = Conversation.objects.get(phone_number=self.phone)
        self.assertEqual(conv.state, 'browsing_products')

    def test_view_product_details(self):
        mock_send = self._patch_send()
        process_message(self.phone, '1')
        process_message(self.phone, '1')
        mock_send.reset_mock()

        process_message(self.phone, '1')

        sent = mock_send.call_args[1]['message']
        self.assertIn('Charger', sent)
        self.assertIn('K100', sent)
        self.assertIn('Add to Cart', sent)

    def test_add_to_cart_and_view_cart(self):
        mock_send = self._patch_send()
        process_message(self.phone, '1')
        process_message(self.phone, '1')
        process_message(self.phone, '1')
        mock_send.reset_mock()

        process_message(self.phone, '1')
        process_message(self.phone, '2')
        process_message(self.phone, '2')

        sent = mock_send.call_args[1]['message']
        self.assertIn('Charger', sent)

    def test_checkout_flow(self):
        mock_send = self._patch_send()
        process_message(self.phone, '1')
        process_message(self.phone, '1')
        process_message(self.phone, '2')
        process_message(self.phone, '1')
        process_message(self.phone, '2')
        process_message(self.phone, '2')
        mock_send.reset_mock()
        
        process_message(self.phone, '1')  # checkout → province list
        process_message(self.phone, '1')  # select province → town list
        process_message(self.phone, '1')  # select town → ask address
        process_message(self.phone, '123 Main Road')  # enter address → ask phone
        process_message(self.phone, '260977000000')  # enter phone → ask delivery
        process_message(self.phone, '1')  # select delivery → ask payment
        process_message(self.phone, '1')  # select payment → order summary
        process_message(self.phone, '1')  # confirm order

        conv = Conversation.objects.get(phone_number=self.phone)
        self.assertEqual(conv.state, 'main_menu')

        msg = WhatsAppMessage.objects.filter(
            conversation=conv, direction='outbound', body__contains='Order Confirmed'
        ).last()
        self.assertIsNotNone(msg)
        self.assertIn('Order Confirmed', msg.body)

    def test_order_status(self):
        mock_send = self._patch_send()
        process_message(self.phone, '3')
        mock_send.reset_mock()

        process_message(self.phone, '00000000-0000-0000-0000-000000000000')

        sent = mock_send.call_args[1]['message']
        self.assertIn('Order not found', sent)

    def test_back_to_main_menu(self):
        mock_send = self._patch_send()
        process_message(self.phone, '1')
        process_message(self.phone, '0')
        mock_send.reset_mock()

        process_message(self.phone, '3')

        sent = mock_send.call_args[1]['message']
        self.assertIn('order ID', sent)
