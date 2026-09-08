export type MediaItem = {
  type: 'photo' | 'video'
  url: string
  filename: string
  mimeType?: string
}

export type SupportedSource = 'instagram' | 'threads'

export type ResolveResult = {
  source: SupportedSource
  inputUrl: string
  items: MediaItem[]
  warnings: string[]
}

export type ApiErrorCode =
  | 'UNAUTHORIZED'
  | 'INVALID_JSON'
  | 'MISSING_URL'
  | 'UNSUPPORTED_URL'
  | 'RESOLVE_FAILED'
  | 'NO_MEDIA_FOUND'
  | 'TIMEOUT'
  | 'RATE_LIMITED'
  | 'INTERNAL_ERROR'

export type ApiErrorResponse = {
  status: 'error'
  code: ApiErrorCode
  message: string
}

export type ApiSuccessResponse = ResolveResult & {
  status: 'ok'
}

export type NormalizedInstagramUrl = {
  source: 'instagram'
  url: string
  shortcode: string
  kind: 'p' | 'reel' | 'tv'
}

export type NormalizedThreadsUrl = {
  source: 'threads'
  url: string
  username: string
  shortcode: string
  kind: 'post'
}

export type NormalizedSourceUrl = NormalizedInstagramUrl | NormalizedThreadsUrl

export type NormalizeResult =
  | {
      ok: true
      value: NormalizedSourceUrl
    }
  | {
      ok: false
      reason: string
    }

export interface MediaResolverProvider {
  name: string
  canHandle(url: string): boolean
  resolve(url: string): Promise<ResolveResult>
}
