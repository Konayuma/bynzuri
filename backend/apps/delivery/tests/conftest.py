import pytest
from apps.delivery.models import Province


@pytest.fixture
def province():
    return Province.objects.create(name='Lusaka', slug='lusaka', sort_order=1)
