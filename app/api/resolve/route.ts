import { authenticate } from '@/lib/auth'
import { ResolveError } from '@/lib/htmlMedia'
import { checkRateLimit } from '@/lib/rateLimit'
import { resolveSupportedUrl } from '@/lib/resolver'
import { errorResponse } from '@/lib/response'
import { normalizeSupportedUrl } from '@/lib/url'

export const runtime = 'nodejs'

export async function POST(req: Request) {
  try {
    const auth = authenticate(req)
    if (!auth.ok) return errorResponse('UNAUTHORIZED', 401)

    const rate = checkRateLimit(auth.token)
    if (!rate.ok) return errorResponse('RATE_LIMITED', 429)

    let body: unknown
    try {
      body = await req.json()
    } catch {
      return errorResponse('INVALID_JSON', 400)
    }

    const inputUrl = body && typeof body === 'object' && 'url' in body ? body.url : undefined
    if (typeof inputUrl !== 'string' || !inputUrl.trim()) {
      return errorResponse('MISSING_URL', 400)
    }

    const normalized = normalizeSupportedUrl(inputUrl)
    if (!normalized.ok) {
      return errorResponse('UNSUPPORTED_URL', 400)
    }

    const result = await resolveSupportedUrl(normalized.value.url)
    if (!result.items.length) {
      return errorResponse('NO_MEDIA_FOUND', 404)
    }

    return Response.json({
      status: 'ok',
      ...result
    })
  } catch (error) {
    if (error instanceof ResolveError) {
      const status = error.code === 'TIMEOUT' ? 504 : 502
      return errorResponse(error.code, status)
    }

    return errorResponse('INTERNAL_ERROR', 500)
  }
}
