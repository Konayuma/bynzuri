// Keep session cookies first-party when Pages and the API use different sites.
// The upstream is configured by the site owner, never by the request.
export async function onRequest({ request, env }) {
  let base
  try {
    base = new URL(env.VITE_API_BASE_URL)
    if (base.protocol !== 'https:' || base.username || base.password || base.search || base.hash || !/^\/api\/?$/.test(base.pathname)) throw new Error('Invalid API URL')
  } catch {
    return new Response('Session service is not configured.', { status: 503 })
  }

  const incoming = new URL(request.url)
  const upstream = new URL(incoming.pathname + incoming.search, base.origin)
  const headers = new Headers(request.headers)
  headers.delete('host')
  const response = await fetch(upstream, {
    method: request.method,
    headers,
    body: ['GET', 'HEAD'].includes(request.method) ? undefined : request.body,
    redirect: 'manual'
  })
  return new Response(response.body, response)
}
