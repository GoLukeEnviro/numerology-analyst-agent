import { BrowserRouter, Route, Routes, useNavigate, useParams } from "react-router-dom";

import type { ProfileCalculationResult } from "./api/types";
import { AnalysisWizard } from "./features/analysis/AnalysisWizard";
import { NumberAtlas, type AtlasNumber } from "./features/profile/NumberAtlas";

function HomePage() {
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

function SiteHeader() {
  return (
    <header className="site-header">
      <a className="brand" href="/" aria-label="Numra Startseite">
        <span className="brand-mark" aria-hidden="true">N</span>
        <span>Numra</span>
      </a>
      <nav aria-label="Hauptnavigation">
        <a href="/wissen">Methode</a>
        <a href="/bibliothek">Bibliothek</a>
        <a href="/datenschutz">Datenschutz</a>
      </nav>
    </header>
  );
}

function NewAnalysisPage() {
  const navigate = useNavigate();
  const complete = (result: ProfileCalculationResult) => {
    const id = result.deterministic_hash.slice(0, 12);
    sessionStorage.setItem(`numra:session:${id}`, JSON.stringify(result));
    void navigate(`/profil/${id}`);
  };
  return (
    <div className="app-shell">
      <SiteHeader />
      <main><AnalysisWizard onComplete={complete} /></main>
    </div>
  );
}

function readSessionProfile(id: string | undefined): ProfileCalculationResult | null {
  if (id === undefined) return null;
  const value = sessionStorage.getItem(`numra:session:${id}`);
  if (value === null) return null;
  try {
    return JSON.parse(value) as ProfileCalculationResult;
  } catch {
    return null;
  }
}

function ProfilePage() {
  const { id } = useParams();
  const result = readSessionProfile(id);
  if (result === null) {
    return (
      <div className="app-shell">
        <SiteHeader />
        <main className="empty-state">
          <p className="eyebrow">PROFIL NICHT VERFÜGBAR</p>
          <h1>Dieser Atlas liegt nicht in deiner aktuellen Sitzung.</h1>
          <a className="button button-primary" href="/analyse/neu">Neue Analyse</a>
        </main>
      </div>
    );
  }
  const numbers: AtlasNumber[] = [
    { label: "Lebensweg", value: result.life_path_a.reduced_value, notation: result.life_path_a.compound_notation },
    { label: "Geburtstag", value: result.birthday.reduced_value, notation: result.birthday.compound_notation },
    { label: "Einstellung", value: result.attitude.reduced_value, notation: result.attitude.compound_notation },
    { label: "Ausdruck", value: result.core_name.expression.reduced_value, notation: result.core_name.expression.compound_notation },
    { label: "Seelenstreben", value: result.core_name.soul_urge.reduced_value, notation: result.core_name.soul_urge.compound_notation },
    { label: "Persönlichkeit", value: result.core_name.personality.reduced_value, notation: result.core_name.personality.compound_notation },
    { label: "Reife", value: result.maturity.reduced_value, notation: result.maturity.compound_notation },
  ];
  return (
    <div className="app-shell">
      <SiteHeader />
      <main className="profile-page">
        <header className="profile-intro">
          <div>
            <p className="eyebrow">DETERMINISTISCHES PROFIL</p>
            <h1>{result.input_ref.core_name}</h1>
            <p>Berechnet für den Stand {result.input_ref.as_of_date}. Keine Deutung verändert diese Werte.</p>
          </div>
          <div className="profile-seal"><span>Schema</span><strong>V2</strong><small>verifiziert</small></div>
        </header>
        <NumberAtlas hash={result.deterministic_hash} numbers={numbers} />
        <section className="result-section">
          <div className="section-heading">
            <div><p className="eyebrow">ZEITLICHE MUSTER</p><h2>Persönliche Zyklen</h2></div>
          </div>
          <div className="cycle-strip">
            <article><span>Jahr</span><strong>{result.cycles.personal_year.reduced_value}</strong></article>
            <article><span>Monat</span><strong>{result.cycles.personal_month.reduced_value}</strong></article>
            <article><span>Tag</span><strong>{result.cycles.personal_day.reduced_value}</strong></article>
          </div>
          <div className="phase-grid">
            <div>
              <h3>Pinnacles</h3>
              {result.cycles.pinnacles.map((phase) => <p key={phase.ordinal}><span>Phase {phase.ordinal}</span><strong>{phase.number.reduced_value}</strong><small>{phase.start_age}–{phase.end_age ?? "offen"} Jahre</small></p>)}
            </div>
            <div>
              <h3>Challenges</h3>
              {result.cycles.challenges.map((phase) => <p key={phase.ordinal}><span>Phase {phase.ordinal}</span><strong>{phase.number.reduced_value}</strong><small>{phase.start_age}–{phase.end_age ?? "offen"} Jahre</small></p>)}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyse/neu" element={<NewAnalysisPage />} />
        <Route path="/profil/:id" element={<ProfilePage />} />
        <Route path="*" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  );
}
