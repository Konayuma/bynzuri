import { afterEach, describe, expect, it, vi } from 'vitest'
import { onRequest } from '../../../functions/sitemap.xml.js'
import worker from '../../../worker.js'

const env = { VITE_API_BASE_URL: 'https://api.example.com/api' }
afterEach(() => vi.unstubAllGlobals())

describe('sitemap route', () => {
  it('proxies the XML from the configured API without forwarding user credentials', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response('<urlset/>', { headers: { 'Content-Type': 'application/xml' } }))
    vi.stubGlobal('fetch', fetch)
    const result = await worker.fetch(new Request('https://bynzuri.com/sitemap.xml', { headers: { Cookie: 'private=value' } }), env)
    expect(result.status).toBe(200)
    expect(await result.text()).toBe('<urlset/>')
    expect(String(fetch.mock.calls[0][0])).toBe('https://api.example.com/api/sitemap/')
    expect(fetch.mock.calls[0][1].headers).toBeUndefined()
  })

  it('returns an error instead of serving an incomplete sitemap when the API fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('unavailable', { status: 503 })))
    const result = await onRequest({ request: new Request('https://bynzuri.com/sitemap.xml'), env })
    expect(result.status).toBe(503)
    expect(result.headers.get('cache-control')).toBe('no-store')
  })

  it('rejects unsafe configuration and unsupported methods', async () => {
    expect((await onRequest({ request: new Request('https://bynzuri.com/sitemap.xml'), env: { VITE_API_BASE_URL: 'http://api.example.com/api' } })).status).toBe(503)
    expect((await onRequest({ request: new Request('https://bynzuri.com/sitemap.xml', { method: 'POST' }), env })).status).toBe(405)
  })
})
