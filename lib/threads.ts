import { extractMediaItemsFromHtml, fetchPublicHtml, ResolveError } from './htmlMedia'
import type { MediaResolverProvider, ResolveResult } from './types'
import { normalizeThreadsUrl } from './url'

export const ThreadsHtmlProvider: MediaResolverProvider = {
  name: 'ThreadsHtmlProvider',
  canHandle(url: string) {
    return normalizeThreadsUrl(url).ok
  },
  async resolve(url: string) {
    const normalized = normalizeThreadsUrl(url)
    if (!normalized.ok || normalized.value.source !== 'threads') {
      throw new ResolveError('RESOLVE_FAILED', 'Unsupported Threads URL.')
    }

    const html = await fetchPublicHtml(normalized.value.url)
    const items = extractMediaItemsFromHtml(html, normalized.value)

    return {
      source: 'threads',
      inputUrl: normalized.value.url,
      items,
      warnings: []
    }
  }
}

export async function resolveThreadsUrl(inputUrl: string): Promise<ResolveResult> {
  return ThreadsHtmlProvider.resolve(inputUrl)
}
