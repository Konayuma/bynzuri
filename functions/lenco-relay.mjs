import { timingSafeEqual } from 'node:crypto';

const error = (status, message) => Response.json({ status: false, message }, { status });

export default {
  async fetch(request) {
    const secret = process.env.LENCO_RELAY_SECRET;
    const supplied = request.headers.get('x-relay-secret') ?? '';
    if (!secret || !supplied) return error(401, 'Unauthorized');
    const expected = Buffer.from(secret);
    const actual = Buffer.from(supplied);
    if (expected.length !== actual.length || !timingSafeEqual(expected, actual)) return error(401, 'Unauthorized');

    const url = new URL(request.url);
    const collection = request.method === 'POST' && url.pathname === '/collections/mobile-money';
    const status = request.method === 'GET' && /^\/collections\/status\/[A-Za-z0-9_.-]{1,100}$/.test(url.pathname);
    if ((!collection && !status) || url.search) return error(404, 'Not found');
    const authorization = request.headers.get('authorization') || '';
    if (!/^Bearer \S+$/.test(authorization)) return error(400, 'Invalid authorization');

    let body;
    if (collection) {
      if (Number(request.headers.get('content-length') || 0) > 4096) return error(413, 'Request too large');
      body = await request.text();
      if (Buffer.byteLength(body) > 4096) return error(413, 'Request too large');
      try {
        const data = JSON.parse(body);
        if (!data || Array.isArray(data) || typeof data !== 'object') throw new Error();
      } catch { return error(400, 'Invalid JSON'); }
    }
    try {
      const response = await fetch(`https://api.lenco.co/access/v2${url.pathname}`, {
        method: request.method,
        headers: { Authorization: authorization, 'Content-Type': 'application/json', Accept: 'application/json', 'User-Agent': 'bynzurisite-backend/1.0' },
        body,
        redirect: 'error',
        signal: AbortSignal.timeout(20000),
      });
      const result = await response.text();
      return new Response(result, { status: response.status, headers: {
        'Content-Type': response.headers.get('content-type') || 'application/json',
        'X-Lenco-Relay': 'upstream', 'Cache-Control': 'no-store',
      } });
    } catch {
      return error(502, 'Upstream request failed');
    }
  },
};
