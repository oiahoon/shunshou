import { getMaxItemsPerRequest, getRequestTimeoutMs } from './config'
import type { MediaItem, NormalizedSourceUrl } from './types'
import { normalizeSupportedUrl } from './url'

const USER_AGENT =
  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'

const HTML_HEADERS = {
  'User-Agent': USER_AGENT,
  Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.9'
}

const MEDIA_URL_PATTERN = /^https:\/\/.+/i
const IMAGE_EXTENSION_PATTERN = /\.(jpe?g|png|webp)(?:[?#]|$)/i
const VIDEO_EXTENSION_PATTERN = /\.mp4(?:[?#]|$)/i
const VIDEO_HINT_PATTERN = /(video|mp4|fbcdn\.net|cdninstagram)/i
const IMAGE_HINT_PATTERN = /(image|photo|display|thumbnail|jpg|jpeg|png|webp|cdninstagram|fbcdn\.net)/i

type Candidate = {
  url: string
  type: MediaItem['type']
  sourceKey?: string
}

export class ResolveError extends Error {
  constructor(
    readonly code: 'TIMEOUT' | 'RESOLVE_FAILED',
    message: string
  ) {
    super(message)
    this.name = 'ResolveError'
  }
}

export async function fetchPublicHtml(url: string) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), getRequestTimeoutMs())

  try {
    let currentUrl = url

    for (let redirectCount = 0; redirectCount < 3; redirectCount += 1) {
      const response = await fetch(currentUrl, {
        headers: HTML_HEADERS,
        redirect: 'manual',
        signal: controller.signal
      })

      if (response.status >= 300 && response.status < 400) {
        const location = response.headers.get('location')
        if (!location) break

        const nextUrl = new URL(location, currentUrl).toString()
        const normalized = normalizeSupportedUrl(nextUrl)
        if (!normalized.ok) {
          throw new ResolveError('RESOLVE_FAILED', 'Provider redirected to an unsupported URL.')
        }

        currentUrl = normalized.value.url
        continue
      }

      if (!response.ok) {
        throw new ResolveError('RESOLVE_FAILED', `Provider returned HTTP ${response.status}.`)
      }

      return await response.text()
    }

    throw new ResolveError('RESOLVE_FAILED', 'Too many redirects while resolving media.')
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ResolveError('TIMEOUT', 'Timed out while fetching public HTML.')
    }

    if (error instanceof ResolveError) throw error
    throw new ResolveError('RESOLVE_FAILED', 'Failed to fetch public HTML.')
  } finally {
    clearTimeout(timeout)
  }
}

export function extractMediaItemsFromHtml(html: string, source: NormalizedSourceUrl) {
  const candidates = [...extractOpenGraphCandidates(html), ...extractJsonCandidates(html)]
  return normalizeCandidates(candidates, source)
}

function extractOpenGraphCandidates(html: string): Candidate[] {
  const candidates: Candidate[] = []
  const metaPattern = /<meta\s+[^>]*>/gi
  const tags = html.match(metaPattern) ?? []

  for (const tag of tags) {
    const property = getAttribute(tag, 'property') ?? getAttribute(tag, 'name')
    const content = getAttribute(tag, 'content')
    if (!property || !content) continue

    const key = property.toLowerCase()
    if (
      key === 'og:video' ||
      key === 'og:video:url' ||
      key === 'og:video:secure_url' ||
      key === 'twitter:player' ||
      key === 'twitter:player:stream'
    ) {
      candidates.push({
        url: decodeHtmlEntities(content),
        type: 'video',
        sourceKey: key
      })
    }

    if (key === 'og:image' || key === 'twitter:image') {
      candidates.push({
        url: decodeHtmlEntities(content),
        type: 'photo',
        sourceKey: key
      })
    }
  }

  return candidates
}

function getAttribute(tag: string, attributeName: string) {
  const pattern = new RegExp(`${attributeName}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i')
  const match = tag.match(pattern)
  return match?.[2] ?? match?.[3] ?? match?.[4]
}

function extractJsonCandidates(html: string): Candidate[] {
  const candidates: Candidate[] = []
  const scriptPattern = /<script\b[^>]*>([\s\S]*?)<\/script>/gi
  const scripts = html.matchAll(scriptPattern)

  for (const script of scripts) {
    const rawContent = decodeHtmlEntities(script[1]?.trim() ?? '')
    if (!rawContent) continue

    const jsonValues = parsePossibleJsonBlocks(rawContent)
    for (const value of jsonValues) {
      collectMediaCandidates(value, candidates)
    }

    collectRegexCandidates(rawContent, candidates)
  }

  return candidates
}

function parsePossibleJsonBlocks(content: string): unknown[] {
  const blocks: unknown[] = []
  const candidates = [content]

  const assignmentMatch = content.match(/=\s*({[\s\S]*}|\[[\s\S]*\])\s*;?$/)
  if (assignmentMatch?.[1]) candidates.push(assignmentMatch[1])

  for (const candidate of candidates) {
    const trimmed = candidate.trim()
    if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) continue

    try {
      blocks.push(JSON.parse(trimmed))
    } catch {
      continue
    }
  }

  return blocks
}

function collectMediaCandidates(value: unknown, candidates: Candidate[], keyHint = '') {
  if (Array.isArray(value)) {
    for (const item of value) collectMediaCandidates(item, candidates, keyHint)
    return
  }

  if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) {
      if (typeof child === 'string') {
        const decoded = decodeEscapedUrl(child)
        const type = inferMediaType(decoded, key)
        if (type) {
          candidates.push({
            url: decoded,
            type,
            sourceKey: key
          })
        }
      } else {
        collectMediaCandidates(child, candidates, key)
      }
    }
  } else if (typeof value === 'string') {
    const decoded = decodeEscapedUrl(value)
    const type = inferMediaType(decoded, keyHint)
    if (type) {
      candidates.push({
        url: decoded,
        type,
        sourceKey: keyHint
      })
    }
  }
}

function collectRegexCandidates(content: string, candidates: Candidate[]) {
  const mediaFieldPattern =
    /"(video_url|playable_url|playable_url_quality_hd|display_url|thumbnail_src|url|src)"\s*:\s*"((?:https?:)?(?:\\?\/){2}[^"]+)"/gi

  for (const match of content.matchAll(mediaFieldPattern)) {
    const key = match[1] ?? ''
    const rawUrl = match[2] ?? ''
    const url = decodeEscapedUrl(rawUrl)
    const type = inferMediaType(url, key)

    if (type) {
      candidates.push({
        url,
        type,
        sourceKey: key
      })
    }
  }
}

function normalizeCandidates(candidates: Candidate[], source: NormalizedSourceUrl): MediaItem[] {
  const seen = new Set<string>()
  const mediaItems: MediaItem[] = []

  for (const candidate of candidates) {
    const url = normalizeMediaUrl(candidate.url)
    if (!url || seen.has(url)) continue

    seen.add(url)
    mediaItems.push({
      type: candidate.type,
      url,
      filename: '',
      mimeType: candidate.type === 'video' ? 'video/mp4' : mimeTypeForImage(url)
    })
  }

  const sorted = mediaItems.sort((a, b) => {
    if (a.type === b.type) return 0
    return a.type === 'video' ? -1 : 1
  })

  const videoOnly = source.source === 'instagram' && (source.kind === 'reel' || source.kind === 'tv')
  const preferred = videoOnly ? sorted.filter((item) => item.type === 'video') : sorted

  return preferred.slice(0, getMaxItemsPerRequest()).map((item, index) => ({
    ...item,
    filename: filenameForMediaItem(item, source, index)
  }))
}

function normalizeMediaUrl(input: string) {
  const decoded = decodeEscapedUrl(input)
  if (!MEDIA_URL_PATTERN.test(decoded)) return null
  if (!inferMediaType(decoded)) return null

  try {
    const parsed = new URL(decoded)
    if (parsed.protocol !== 'https:') return null
    if (parsed.username || parsed.password) return null
    if (isPlatformStaticAsset(parsed)) return null
    return parsed.toString()
  } catch {
    return null
  }
}

function isPlatformStaticAsset(url: URL) {
  const hostname = url.hostname.toLowerCase()
  const pathname = url.pathname.toLowerCase()

  if (hostname === 'static.cdninstagram.com') return true
  if (pathname.includes('/rsrc.php')) return true
  if (hostname.endsWith('.fbcdn.net') && pathname.includes('/rsrc.php')) return true

  return false
}

function inferMediaType(url: string, keyHint = ''): MediaItem['type'] | null {
  if (!url || !MEDIA_URL_PATTERN.test(url)) return null

  if (VIDEO_EXTENSION_PATTERN.test(url)) return 'video'
  if (IMAGE_EXTENSION_PATTERN.test(url)) return 'photo'

  const hint = `${keyHint} ${url}`
  if (VIDEO_HINT_PATTERN.test(hint) && /video|playable/i.test(hint)) return 'video'
  if (IMAGE_HINT_PATTERN.test(hint) && /(image|photo|display|thumbnail)/i.test(hint)) return 'photo'

  return null
}

function filenameForMediaItem(item: MediaItem, source: NormalizedSourceUrl, index: number) {
  const extension = item.type === 'video' ? 'mp4' : imageExtension(item.url)

  if (source.source === 'instagram') {
    if (source.kind === 'reel' && item.type === 'video') {
      return `instagram-reel-${source.shortcode}.${extension}`
    }

    return `instagram-${item.type === 'video' ? 'video' : 'photo'}-${source.shortcode}-${index + 1}.${extension}`
  }

  return `threads-${item.type === 'video' ? 'video' : 'photo'}-${source.username}-${source.shortcode}-${index + 1}.${extension}`
}

function imageExtension(url: string) {
  const match = url.match(/\.(jpe?g|png|webp)(?:[?#]|$)/i)
  const extension = match?.[1]?.toLowerCase() ?? 'jpg'
  return extension === 'jpeg' ? 'jpg' : extension
}

function mimeTypeForImage(url: string) {
  const extension = imageExtension(url)
  if (extension === 'png') return 'image/png'
  if (extension === 'webp') return 'image/webp'
  return 'image/jpeg'
}

function decodeEscapedUrl(value: string) {
  return decodeHtmlEntities(value)
    .replace(/^\/\//, 'https://')
    .replace(/\\\//g, '/')
    .replace(/\\u0026/g, '&')
}

function decodeHtmlEntities(value: string) {
  return value
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#x27;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
}
