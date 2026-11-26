// Both Pages Functions and the static-assets Worker use this route.
export async function onRequest({ request, env }) {
  if (!['GET', 'HEAD'].includes(request.method)) {
    return new Response('Method not allowed', { status: 405, headers: { Allow: 'GET, HEAD' } })
  }
  let upstream
  try {
    const base = new URL(env.VITE_API_BASE_URL)
    if (base.protocol !== 'https:' || base.username || base.password || base.search || base.hash || !/^\/api\/?$/.test(base.pathname)) throw new Error('Invalid API URL')
    upstream = new URL('/api/sitemap/', base.origin)
  } catch {
    return new Response('Sitemap service is not configured.', { status: 503 })
  }
  try {
    const response = await fetch(upstream, { method: request.method, redirect: 'error' })
    if (!response.ok || !response.headers.get('content-type')?.toLowerCase().includes('application/xml')) {
      return new Response('Sitemap temporarily unavailable.', { status: 503, headers: { 'Cache-Control': 'no-store' } })
    }
    return new Response(request.method === 'HEAD' ? null : response.body, {
      status: 200,
      headers: { 'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'public, max-age=300' },
    })
  } catch {
    return new Response('Sitemap temporarily unavailable.', { status: 503, headers: { 'Cache-Control': 'no-store' } })
  }
}
