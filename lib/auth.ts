import { getApiTokens } from './config'

type AuthResult =
  | {
      ok: true
      token: string
    }
  | {
      ok: false
    }

export function authenticate(req: Request): AuthResult {
  const header = req.headers.get('authorization')
  if (!header) return { ok: false }

  const match = header.match(/^Bearer\s+(.+)$/i)
  if (!match) return { ok: false }

  const token = match[1]?.trim()
  if (!token) return { ok: false }

  const allowedTokens = getApiTokens()
  if (!allowedTokens.includes(token)) return { ok: false }

  return {
    ok: true,
    token
  }
}

export function redactToken(token: string) {
  return `${token.slice(0, 6)}...`
}
