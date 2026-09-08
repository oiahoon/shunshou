import { InstagramHtmlProvider } from './instagram'
import { ThreadsHtmlProvider } from './threads'
import type { MediaResolverProvider, ResolveResult } from './types'
import { normalizeSupportedUrl } from './url'

const providers: MediaResolverProvider[] = [InstagramHtmlProvider, ThreadsHtmlProvider]

export async function resolveSupportedUrl(inputUrl: string): Promise<ResolveResult> {
  const normalized = normalizeSupportedUrl(inputUrl)
  if (!normalized.ok) {
    throw new Error('Unsupported URL.')
  }

  const provider = providers.find((candidate) => candidate.canHandle(normalized.value.url))
  if (!provider) {
    throw new Error('No provider available for URL.')
  }

  return provider.resolve(normalized.value.url)
}
