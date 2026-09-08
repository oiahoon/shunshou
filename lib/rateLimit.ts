const WINDOW_MS = 60 * 60 * 1000
const DEFAULT_LIMIT = 30

type Bucket = {
  count: number
  resetAt: number
}

const buckets = new Map<string, Bucket>()

export type RateLimitResult =
  | {
      ok: true
      remaining: number
      resetAt: number
    }
  | {
      ok: false
      resetAt: number
    }

export function checkRateLimit(token: string, now = Date.now(), limit = DEFAULT_LIMIT): RateLimitResult {
  const existing = buckets.get(token)

  if (!existing || existing.resetAt <= now) {
    const resetAt = now + WINDOW_MS
    buckets.set(token, {
      count: 1,
      resetAt
    })

    return {
      ok: true,
      remaining: limit - 1,
      resetAt
    }
  }

  if (existing.count >= limit) {
    return {
      ok: false,
      resetAt: existing.resetAt
    }
  }

  existing.count += 1

  return {
    ok: true,
    remaining: limit - existing.count,
    resetAt: existing.resetAt
  }
}

export function resetRateLimitForTests() {
  buckets.clear()
}
