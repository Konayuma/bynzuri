declare const worker: { fetch(request: Request, env: { VITE_API_BASE_URL?: string }): Promise<Response> }
export default worker
