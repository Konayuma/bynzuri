from unittest.mock import Mock, patch

from django.test import override_settings

from apps.payments.lenco import lenco_service


@override_settings(LENCO_API_KEY='provider-key', LENCO_RELAY_URL='')
def test_direct_collection_uses_provider_recommended_user_agent():
    response = Mock(status_code=200, ok=True)
    response.json.return_value = {'status': True}
    with patch('apps.payments.lenco.requests.request', return_value=response) as request:
        lenco_service.initiate_collection(2, 'reference', '260971111111', 'mtn')
    assert request.call_args.kwargs['headers']['User-Agent'] == 'bynzurisite-backend/1.0'


@override_settings(LENCO_API_KEY='provider-key', LENCO_RELAY_URL='https://relay.example', LENCO_RELAY_SECRET='relay-secret')
def test_relay_authentication_failure_is_uncertain():
    response = Mock(status_code=401, headers={})
    with patch('apps.payments.lenco.requests.request', return_value=response) as request:
        result = lenco_service.get_collection_status('ref')
    assert result['uncertain'] is True
    assert request.call_args.args[1] == 'https://relay.example/collections/status/ref'
    assert request.call_args.kwargs['headers']['X-Relay-Secret'] == 'relay-secret'


@override_settings(LENCO_API_KEY='provider-key', LENCO_RELAY_URL='https://relay.example', LENCO_RELAY_SECRET='relay-secret')
def test_upstream_denial_remains_a_provider_denial():
    response = Mock(status_code=403, ok=False, headers={'X-Lenco-Relay': 'upstream'})
    response.json.return_value = {'errorCode': '13'}
    with patch('apps.payments.lenco.requests.request', return_value=response):
        result = lenco_service.get_collection_status('ref')
    assert result['rejected'] is True
    assert result['access_denied'] is True


@override_settings(LENCO_API_KEY='provider-key', LENCO_RELAY_URL='http://relay.example', LENCO_RELAY_SECRET='relay-secret')
def test_relay_requires_https():
    with patch('apps.payments.lenco.requests.request') as request:
        assert lenco_service.get_collection_status('ref')['uncertain'] is True
        request.assert_not_called()
