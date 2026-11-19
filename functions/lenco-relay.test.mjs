import { test, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import relay from './lenco-relay.mjs';

const realFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = realFetch; });
process.env.LENCO_RELAY_SECRET = 'relay-test-secret';
const headers = { 'x-relay-secret': 'relay-test-secret', authorization: 'Bearer provider-token' };

test('rejects unauthenticated requests and arbitrary destinations', async () => {
  assert.equal((await relay.fetch(new Request('https://relay/collections/mobile-money', { method: 'POST' }))).status, 401);
  assert.equal((await relay.fetch(new Request('https://relay/transfers', { headers }))).status, 404);
  assert.equal((await relay.fetch(new Request('https://relay/collections/status/ref?x=1', { headers }))).status, 404);
});

test('relays only the fixed Lenco endpoint and preserves upstream status', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'https://api.lenco.co/access/v2/collections/mobile-money');
    assert.equal(options.headers.Authorization, 'Bearer provider-token');
    assert.equal(options.redirect, 'error');
    return new Response('{"errorCode":"13"}', { status: 403 });
  };
  const response = await relay.fetch(new Request('https://relay/collections/mobile-money', {
    method: 'POST', headers, body: '{"amount":1}',
  }));
  assert.equal(response.status, 403);
  assert.equal(response.headers.get('x-lenco-relay'), 'upstream');
  assert.deepEqual(await response.json(), { errorCode: '13' });
});

test('upstream transport errors are not marked as provider rejections', async () => {
  globalThis.fetch = async () => { throw new Error('network failure'); };
  const response = await relay.fetch(new Request('https://relay/collections/status/reference-1', { headers }));
  assert.equal(response.status, 502);
  assert.equal(response.headers.get('x-lenco-relay'), null);
});
