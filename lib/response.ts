import type { ApiErrorCode, ApiErrorResponse } from './types'

const errorMessages: Record<ApiErrorCode, string> = {
  UNAUTHORIZED: 'Missing or invalid authorization token.',
  INVALID_JSON: 'Request body must be valid JSON.',
  MISSING_URL: 'Request body must include a url string.',
  UNSUPPORTED_URL: 'Only public Instagram post, Reel, TV, and Threads post URLs are supported.',
  RESOLVE_FAILED: 'Could not resolve this media.',
  NO_MEDIA_FOUND:
    'Could not resolve media from this URL. It may be private, expired, region-limited, or unsupported.',
  TIMEOUT: 'Timed out while resolving this Instagram URL.',
  RATE_LIMITED: 'Too many requests for this token. Please try again later.',
  INTERNAL_ERROR: 'Unexpected server error.'
}

export function errorBody(code: ApiErrorCode, message = errorMessages[code]): ApiErrorResponse {
  return {
    status: 'error',
    code,
    message
  }
}

export function errorResponse(code: ApiErrorCode, status: number, message?: string) {
  return Response.json(errorBody(code, message), { status })
}
