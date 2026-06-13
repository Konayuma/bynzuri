import pytest
from django.contrib.auth import get_user_model
from apps.users.models import Address

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username='test@bynzuri.com',
            email='test@bynzuri.com',
            password='testpass123',
            first_name='Jane',
            last_name='Doe'
        )
        assert user.email == 'test@bynzuri.com'
        assert user.first_name == 'Jane'
        assert user.role == 'customer'
        assert user.is_active is True
        assert str(user) == 'test@bynzuri.com'

    def test_create_admin(self):
        admin = User.objects.create_superuser(
            username='admin@bynzuri.com',
            email='admin@bynzuri.com',
            password='admin123'
        )
        assert admin.role == 'admin'
        assert admin.is_staff is True

    def test_user_email_unique(self):
        User.objects.create_user(username='dup@bynzuri.com', email='dup@bynzuri.com', password='test123')
        with pytest.raises(Exception):
            User.objects.create_user(username='dup@bynzuri.com', email='dup@bynzuri.com', password='test456')

    def test_user_defaults(self):
        user = User.objects.create_user(username='defaults@bynzuri.com', email='defaults@bynzuri.com', password='test123')
        assert user.phone == ''
        assert user.role == 'customer'


@pytest.mark.django_db
class TestAddressModel:
    def test_create_address(self, user):
        address = Address.objects.create(
            user=user,
            province='Lusaka',
            town='Lusaka',
            street_address='123 Main Road',
            phone='260977000000'
        )
        assert address.province == 'Lusaka'
        assert str(address) == '123 Main Road, Lusaka, Lusaka'

    def test_default_address(self, user):
        addr1 = Address.objects.create(user=user, province='Lusaka', town='Lusaka',
                                        street_address='Addr 1', phone='260977000000', is_default=True)
        addr2 = Address.objects.create(user=user, province='Copperbelt', town='Kitwe',
                                        street_address='Addr 2', phone='260977000001', is_default=False)
        assert addr1.is_default is True
        assert addr2.is_default is False
