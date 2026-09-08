const endpoints = ['GET /api/health', 'POST /api/resolve']

export default function Home() {
  return (
    <main className="shell">
      <section className="panel" aria-labelledby="title">
        <p className="label">Private API</p>
        <h1 id="title">Instagram to WeChat Share Helper</h1>
        <p className="summary">This is a private helper API for iOS Shortcuts.</p>

        <div className="section">
          <h2>Available endpoints</h2>
          <ul>
            {endpoints.map((endpoint) => (
              <li key={endpoint}>
                <code>{endpoint}</code>
              </li>
            ))}
          </ul>
        </div>

        <p className="notice">This service does not store, cache, or proxy media files.</p>
      </section>
    </main>
  )
}
