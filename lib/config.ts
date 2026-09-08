const DEFAULT_MAX_ITEMS = 10
const DEFAULT_TIMEOUT_MS = 8000

function parsePositiveInteger(value: string | undefined, fallback: number) {
  if (!value) return fallback

  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

export function getApiTokens() {
  return (process.env.API_TOKENS ?? '')
    .split(',')
    .map((token) => token.trim())
    .filter(Boolean)
}

export function getMaxItemsPerRequest() {
  return parsePositiveInteger(process.env.MAX_ITEMS_PER_REQUEST, DEFAULT_MAX_ITEMS)
}

export function getRequestTimeoutMs() {
  return parsePositiveInteger(process.env.REQUEST_TIMEOUT_MS, DEFAULT_TIMEOUT_MS)
}

export function isDebugLoggingEnabled() {
  return process.env.ENABLE_DEBUG_LOGS === 'true'
}
