import { describe, expect, it } from 'vitest'
import { errorBody } from '../lib/response'

describe('errorBody', () => {
  it('returns stable error JSON', () => {
    expect(errorBody('UNSUPPORTED_URL')).toEqual({
      status: 'error',
      code: 'UNSUPPORTED_URL',
      message: 'Only public Instagram post, Reel, TV, and Threads post URLs are supported.'
    })
  })

  it('allows route-specific messages when needed', () => {
    expect(errorBody('INTERNAL_ERROR', 'Custom message')).toEqual({
      status: 'error',
      code: 'INTERNAL_ERROR',
      message: 'Custom message'
    })
  })
})
