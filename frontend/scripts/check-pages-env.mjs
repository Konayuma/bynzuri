// Prevent a deployed Pages build from silently calling a visitor's localhost.
if (process.env.CF_PAGES === '1') {
  const value = process.env.VITE_API_BASE_URL
  let api
  try { api = new URL(value || '') } catch { /* explained below */ }
  if (!api || api.protocol !== 'https:' || !api.hostname || /^(localhost|127\.|\[::1\]$)/i.test(api.hostname) || api.username || api.password || api.search || api.hash || !/\/api\/?$/.test(api.pathname)) {
    console.error('Set VITE_API_BASE_URL to the HTTPS Render API URL ending in /api before building Cloudflare Pages.')
    process.exit(1)
  }
}
