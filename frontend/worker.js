import { onRequest } from './functions/api/auth/[[path]].js'

export default {
  fetch(request, env) {
    return onRequest({ request, env })
  }
}
