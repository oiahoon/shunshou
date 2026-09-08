import { describe, expect, it } from 'vitest'
import { extractMediaItemsFromHtml } from '../lib/htmlMedia'

const instagramReelSource = {
  source: 'instagram',
  url: 'https://www.instagram.com/reel/ABC123/',
  shortcode: 'ABC123',
  kind: 'reel'
} as const

describe('extractMediaItemsFromHtml', () => {
  it('extracts video URLs from JSON inside script tags', () => {
    const html = `
      <html>
        <head>
          <script type="application/json">
            {"video_url":"https:\\/\\/video.cdninstagram.com\\/o1\\/v\\/clip.mp4?token=abc"}
          </script>
        </head>
      </html>
    `

    expect(extractMediaItemsFromHtml(html, instagramReelSource)).toEqual([
      {
        type: 'video',
        url: 'https://video.cdninstagram.com/o1/v/clip.mp4?token=abc',
        filename: 'instagram-reel-ABC123.mp4',
        mimeType: 'video/mp4'
      }
    ])
  })

  it('does not return a Reel cover image as downloadable video media', () => {
    const html = `
      <html>
        <head>
          <meta property = "og:image" content = "https://scontent.cdninstagram.com/v/t51/cover.jpg?x=1" />
          <meta name="twitter:image" content="https://scontent.cdninstagram.com/v/t51/cover.jpg?x=1" />
        </head>
      </html>
    `

    expect(extractMediaItemsFromHtml(html, instagramReelSource)).toEqual([])
  })
})
