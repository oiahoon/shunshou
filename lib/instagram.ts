import { extractMediaItemsFromHtml, fetchPublicHtml, ResolveError } from './htmlMedia'
import type { MediaResolverProvider, ResolveResult } from './types'
import { normalizeInstagramUrl } from './url'

export { ResolveError }

export const InstagramHtmlProvider: MediaResolverProvider = {
  name: 'InstagramHtmlProvider',
  canHandle(url: string) {
    return normalizeInstagramUrl(url).ok
  },
  async resolve(url: string) {
    const normalized = normalizeInstagramUrl(url)
    if (!normalized.ok || normalized.value.source !== 'instagram') {
      throw new ResolveError('RESOLVE_FAILED', 'Unsupported Instagram URL.')
    }

    const html = await fetchPublicHtml(normalized.value.url)
    const items = extractMediaItemsFromHtml(html, normalized.value)
    const warnings = buildInstagramWarnings(normalized.value.kind, items.length)

    return {
      source: 'instagram',
      inputUrl: normalized.value.url,
      items,
      warnings
    }
  }
}

export async function resolveInstagramUrl(inputUrl: string): Promise<ResolveResult> {
  return InstagramHtmlProvider.resolve(inputUrl)
}

function buildInstagramWarnings(kind: 'p' | 'reel' | 'tv', itemCount: number) {
  if ((kind === 'reel' || kind === 'tv') && itemCount === 0) {
    return ['Instagram did not expose a direct video URL in the public HTML.']
  }

  return []
}
