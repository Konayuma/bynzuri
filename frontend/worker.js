import { onRequest } from './functions/api/auth/[[path]].js'
import { onRequest as sitemap } from './functions/sitemap.xml.js'

export default {
  fetch(request, env) {
    if (new URL(request.url).pathname === '/sitemap.xml') return sitemap({ request, env })
    return onRequest({ request, env })
  }
}
