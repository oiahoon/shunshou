import type { NormalizeResult, NormalizedInstagramUrl, NormalizedThreadsUrl } from './types'

const ACCEPTED_INSTAGRAM_HOSTNAMES = new Set([
  'instagram.com',
  'www.instagram.com',
  'm.instagram.com',
  'instagr.am',
  'www.instagr.am'
])

const ACCEPTED_INSTAGRAM_PATH_PATTERN = /^\/(p|reel|reels|tv)\/([A-Za-z0-9_-]+)\/?$/

const ACCEPTED_THREADS_HOSTNAMES = new Set([
  'threads.com',
  'www.threads.com',
  'threads.net',
  'www.threads.net'
])

const ACCEPTED_THREADS_PATH_PATTERN = /^\/@([A-Za-z0-9._]+)\/post\/([A-Za-z0-9_-]+)\/?$/

type ParsedUrlResult =
  | {
      ok: true
      value: URL
    }
  | {
      ok: false
      reason: string
    }

export function normalizeInstagramUrl(input: string): NormalizeResult {
  const parsed = parseSafeHttpUrl(input)
  if (!parsed.ok) return parsed

  const hostname = parsed.value.hostname.toLowerCase()
  if (!ACCEPTED_INSTAGRAM_HOSTNAMES.has(hostname)) {
    return {
      ok: false,
      reason: 'URL host is not supported.'
    }
  }

  const match = parsed.value.pathname.match(ACCEPTED_INSTAGRAM_PATH_PATTERN)
  if (!match) {
    return {
      ok: false,
      reason: 'Instagram path is not a supported post, Reel, or TV URL.'
    }
  }

  const rawKind = match[1]
  const shortcode = match[2]
  const kind = (rawKind === 'reels' ? 'reel' : rawKind) as NormalizedInstagramUrl['kind']

  return {
    ok: true,
    value: {
      source: 'instagram',
      url: `https://www.instagram.com/${kind}/${shortcode}/`,
      shortcode,
      kind
    }
  }
}

export function normalizeThreadsUrl(input: string): NormalizeResult {
  const parsed = parseSafeHttpUrl(input)
  if (!parsed.ok) return parsed

  const hostname = parsed.value.hostname.toLowerCase()
  if (!ACCEPTED_THREADS_HOSTNAMES.has(hostname)) {
    return {
      ok: false,
      reason: 'URL host is not supported.'
    }
  }

  const match = parsed.value.pathname.match(ACCEPTED_THREADS_PATH_PATTERN)
  if (!match) {
    return {
      ok: false,
      reason: 'Threads path is not a supported post URL.'
    }
  }

  const username = match[1]
  const shortcode = match[2]

  return {
    ok: true,
    value: {
      source: 'threads',
      url: `https://www.threads.com/@${username}/post/${shortcode}`,
      username,
      shortcode,
      kind: 'post'
    } satisfies NormalizedThreadsUrl
  }
}

export function normalizeSupportedUrl(input: string): NormalizeResult {
  const instagram = normalizeInstagramUrl(input)
  if (instagram.ok) return instagram

  const threads = normalizeThreadsUrl(input)
  if (threads.ok) return threads

  return {
    ok: false,
    reason: 'Only public Instagram post, Reel, TV, and Threads post URLs are supported.'
  }
}

export function isCanonicalInstagramUrl(input: string) {
  const normalized = normalizeInstagramUrl(input)
  return normalized.ok && normalized.value.url === input
}

function parseSafeHttpUrl(input: string): ParsedUrlResult {
  if (typeof input !== 'string' || !input.trim()) {
    return {
      ok: false,
      reason: 'URL is empty.'
    }
  }

  let parsed: URL
  try {
    parsed = new URL(input.trim())
  } catch {
    return {
      ok: false,
      reason: 'URL is invalid.'
    }
  }

  if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
    return {
      ok: false,
      reason: 'Only HTTP(S) URLs are supported.'
    }
  }

  if (parsed.username || parsed.password) {
    return {
      ok: false,
      reason: 'URLs with embedded credentials are not supported.'
    }
  }

  return {
    ok: true,
    value: parsed
  }
}
