export default function Home() {
  return (
    <main className="cc-auth-layout">
      <div className="cc-card cc-card-pad cc-auth-card">
        <div className="cc-brand" style={{ color: "#172033", marginBottom: 12 }}>
          CARE<span style={{ color: "#3159a8" }}>CIRCLE</span>
        </div>
        <h1 style={{ marginTop: 0 }}>Trusted companionship for your parent</h1>
        <p className="cc-muted">Coordinate safe, non-medical companionship visits with family and trusted companions.</p>
        <div className="cc-actions" style={{ marginTop: 24 }}>
          <a className="cc-button" href="/login">Sign in</a>
          <a className="cc-button secondary" href="/register">Create account</a>
        </div>
      </div>
    </main>
  );
}
