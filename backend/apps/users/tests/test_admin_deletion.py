from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.test import override_settings

from apps.orders.models import Order, OrderEmail
from apps.users.models import EmailVerification
from apps.users.verification import issue_code


@pytest.mark.django_db
@override_settings(STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
def test_user_deletion_allows_verification_cascade_and_preserves_order_history(client):
    User = get_user_model()
    admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='password123')
    customer = User.objects.create_user(username='customer', email='customer@example.com', password='password123')
    challenge = issue_code(customer)
    order = Order.objects.create(user=customer, status='paid', total_amount=Decimal('10'), delivery_fee=Decimal('0'),
        grand_total=Decimal('10'), province='Lusaka', town='Lusaka', street_address='Street',
        phone='260977000000', delivery_method='pickup', payment_method='mtn_momo')
    notification = OrderEmail.objects.create(order=order, event='payment_receipt', recipient=customer.email, payload={})
    client.force_login(admin)
    url = reverse('admin:users_user_delete', args=[customer.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert b'Cannot delete' not in response.content
    assert client.post(url, {'post': 'yes'}).status_code == 302
    assert not User.objects.filter(pk=customer.pk).exists()
    assert not EmailVerification.objects.filter(pk=challenge.pk).exists()
    order.refresh_from_db()
    assert order.user_id is None
    assert OrderEmail.objects.filter(pk=notification.pk, order=order).exists()


@pytest.mark.django_db
def test_verification_records_cannot_be_deleted_directly_and_user_permission_is_required(client):
    User = get_user_model()
    staff = User.objects.create_user(username='staff', email='staff@example.com', password='password123', is_staff=True)
    target = User.objects.create_user(username='target', email='target@example.com', password='password123')
    verification = issue_code(target)
    staff.user_permissions.add(Permission.objects.get(content_type__app_label='users', codename='view_emailverification'))
    client.force_login(staff)
    assert client.get(reverse('admin:users_emailverification_delete', args=[verification.pk])).status_code == 403
    assert client.post(reverse('admin:users_user_delete', args=[target.pk]), {'post': 'yes'}).status_code == 403
    assert User.objects.filter(pk=target.pk).exists()
    assert EmailVerification.objects.filter(pk=verification.pk).exists()


@pytest.mark.django_db
@override_settings(STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
def test_staff_with_user_delete_permission_can_remove_user_but_not_verification_directly(client):
    User = get_user_model()
    staff = User.objects.create_user(username='staff2', email='staff2@example.com', password='password123', is_staff=True)
    staff.user_permissions.add(Permission.objects.get(content_type__app_label='users', codename='delete_user'))
    target = User.objects.create_user(username='target2', email='target2@example.com', password='password123')
    verification = issue_code(target)
    client.force_login(staff)
    assert client.get(reverse('admin:users_emailverification_delete', args=[verification.pk])).status_code == 403
    url = reverse('admin:users_user_delete', args=[target.pk])
    assert b'Cannot delete' not in client.get(url).content
    assert client.post(url, {'post': 'yes'}).status_code == 302
    assert not User.objects.filter(pk=target.pk).exists()
