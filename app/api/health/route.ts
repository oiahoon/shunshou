export const runtime = 'nodejs'

export async function GET() {
  return Response.json({
    status: 'ok',
    service: 'instagram-wechat-helper',
    version: '1.0.0'
  })
}
