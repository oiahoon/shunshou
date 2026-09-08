import { describe, expect, it } from 'vitest'
import { normalizeInstagramUrl, normalizeSupportedUrl, normalizeThreadsUrl } from '../lib/url'

describe('normalizeInstagramUrl', () => {
  it('normalizes Instagram Reel URLs with query parameters', () => {
    const result = normalizeInstagramUrl('https://www.instagram.com/reel/ABC_123/?igsh=abc')

    expect(result).toEqual({
      ok: true,
      value: {
        source: 'instagram',
        url: 'https://www.instagram.com/reel/ABC_123/',
        shortcode: 'ABC_123',
        kind: 'reel'
      }
    })
  })

  it('normalizes plural reels URLs to reel URLs', () => {
    const result = normalizeInstagramUrl('https://m.instagram.com/reels/abc-def/')

    expect(result).toEqual({
      ok: true,
      value: {
        source: 'instagram',
        url: 'https://www.instagram.com/reel/abc-def/',
        shortcode: 'abc-def',
        kind: 'reel'
      }
    })
  })

  it('normalizes post and TV URLs', () => {
    expect(normalizeInstagramUrl('http://instagr.am/p/POST1/')).toMatchObject({
      ok: true,
      value: {
        source: 'instagram',
        url: 'https://www.instagram.com/p/POST1/',
        shortcode: 'POST1',
        kind: 'p'
      }
    })

    expect(normalizeInstagramUrl('https://instagram.com/tv/TV1/')).toMatchObject({
      ok: true,
      value: {
        source: 'instagram',
        url: 'https://www.instagram.com/tv/TV1/',
        shortcode: 'TV1',
        kind: 'tv'
      }
    })
  })

  it('rejects non-Instagram URLs and unsupported Instagram paths', () => {
    expect(normalizeInstagramUrl('https://example.com/reel/ABC/')).toMatchObject({ ok: false })
    expect(normalizeInstagramUrl('https://www.instagram.com/stories/user/123/')).toMatchObject({ ok: false })
    expect(normalizeInstagramUrl('https://www.instagram.com/explore/tags/test/')).toMatchObject({ ok: false })
    expect(normalizeInstagramUrl('https://www.instagram.com/someuser/')).toMatchObject({ ok: false })
  })

  it('rejects URLs with embedded credentials', () => {
    expect(normalizeInstagramUrl('https://user:pass@www.instagram.com/reel/ABC/')).toMatchObject({
      ok: false
    })
  })
})

describe('normalizeThreadsUrl', () => {
  it('normalizes Threads post URLs and removes query parameters', () => {
    const result = normalizeThreadsUrl(
      'https://www.threads.com/@akidataxi/post/DZtinOxkxrH?xmt=test&slof=1'
    )

    expect(result).toEqual({
      ok: true,
      value: {
        source: 'threads',
        url: 'https://www.threads.com/@akidataxi/post/DZtinOxkxrH',
        username: 'akidataxi',
        shortcode: 'DZtinOxkxrH',
        kind: 'post'
      }
    })
  })

  it('accepts threads.net hostnames', () => {
    expect(normalizeThreadsUrl('https://threads.net/@meta/post/ABC123')).toMatchObject({
      ok: true,
      value: {
        source: 'threads',
        url: 'https://www.threads.com/@meta/post/ABC123'
      }
    })
  })

  it('rejects unsupported Threads paths', () => {
    expect(normalizeThreadsUrl('https://www.threads.com/@akidataxi')).toMatchObject({ ok: false })
    expect(normalizeThreadsUrl('https://www.threads.com/t/DZtinOxkxrH')).toMatchObject({ ok: false })
  })
})

describe('normalizeSupportedUrl', () => {
  it('accepts Instagram and Threads URLs', () => {
    expect(normalizeSupportedUrl('https://www.instagram.com/p/POST1/')).toMatchObject({
      ok: true,
      value: { source: 'instagram' }
    })

    expect(normalizeSupportedUrl('https://www.threads.com/@akidataxi/post/DZtinOxkxrH')).toMatchObject({
      ok: true,
      value: { source: 'threads' }
    })
  })

  it('rejects other services', () => {
    expect(normalizeSupportedUrl('https://example.com/post/1')).toMatchObject({ ok: false })
  })
})
