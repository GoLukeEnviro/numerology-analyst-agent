export function App() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="/" aria-label="Numra Startseite">
          <span className="brand-mark" aria-hidden="true">
            N
          </span>
          <span>Numra</span>
        </a>
        <nav aria-label="Hauptnavigation">
          <a href="/wissen">Methode</a>
          <a href="/bibliothek">Bibliothek</a>
          <a href="/datenschutz">Datenschutz</a>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy reveal reveal-one">
            <p className="eyebrow">DEIN PROFIL · DEIN RECHENWEG</p>
            <h1>Numerologie. Nachvollziehbar.</h1>
            <p className="hero-lead">
              Numra trennt überprüfbare Berechnungen von traditionellen Deutungen – damit du
              reflektieren kannst, ohne Behauptungen mit Fakten zu verwechseln.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="/analyse/neu">
                Analyse starten
                <span aria-hidden="true">↗</span>
              </a>
              <a className="button button-quiet" href="/wissen">
                So arbeitet Numra
              </a>
            </div>
            <p className="privacy-note">
              <span aria-hidden="true">⌁</span>
              Profile werden nur auf deinem Gerät gespeichert.
            </p>
          </div>

          <div className="atlas-card reveal reveal-two" aria-label="Beispiel eines Zahlenatlas">
            <div className="atlas-orbit" aria-hidden="true">
              <span className="orbit orbit-outer" />
              <span className="orbit orbit-inner" />
              <span className="atlas-number">1</span>
              <span className="satellite satellite-one">3</span>
              <span className="satellite satellite-two">7</span>
              <span className="satellite satellite-three">5</span>
            </div>
            <div className="atlas-caption">
              <span>Beispielprofil</span>
              <strong>1 · Eigenständigkeit</strong>
            </div>
          </div>
        </section>

        <section className="boundary reveal reveal-three" aria-labelledby="boundary-title">
          <div>
            <p className="eyebrow">TRANSPARENTE AUSSAGEKLASSEN</p>
            <h2 id="boundary-title">Was ist berechnet – und was ist Deutung?</h2>
          </div>
          <div className="claim-grid">
            <article>
              <span className="claim-dot claim-calculation" />
              <h3>Berechnung</h3>
              <p>Deterministisch, versioniert und mit vollständigem Rechenweg.</p>
            </article>
            <article>
              <span className="claim-dot claim-tradition" />
              <h3>Tradition</h3>
              <p>Historisch überlieferte Symbolik, ausdrücklich als solche markiert.</p>
            </article>
            <article>
              <span className="claim-dot claim-hypothesis" />
              <h3>Hypothese</h3>
              <p>Eine Einladung zur Reflexion, nie Diagnose oder Vorhersage.</p>
            </article>
          </div>
          <p className="scientific-boundary">
            Numerologie ist keine wissenschaftlich validierte Persönlichkeitsdiagnostik.
          </p>
        </section>
      </main>
    </div>
  );
}
