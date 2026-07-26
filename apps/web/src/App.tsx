import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes, useNavigate, useParams } from "react-router-dom";

import type { ProfileCalculationResult } from "./api/types";
import { AnalysisWizard } from "./features/analysis/AnalysisWizard";
import { NumberAtlas, type AtlasNumber } from "./features/profile/NumberAtlas";
import { VaultLockedError, parseEncryptedArchive } from "./storage/crypto";
import { localProfiles, type LocalProfile } from "./storage/repository";

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
    const id = result.deterministic_hash.slice(0, 16);
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
  const [result, setResult] = useState(() => readSessionProfile(id));
  const [loading, setLoading] = useState(result === null);
  const [message, setMessage] = useState("");
  useEffect(() => {
    if (result !== null || id === undefined) return;
    void localProfiles
      .getProfile(id)
      .then((saved) => setResult(saved?.profile ?? null))
      .catch((error: unknown) =>
        setMessage(error instanceof VaultLockedError ? error.message : "Das Profil konnte nicht geladen werden."),
      )
      .finally(() => setLoading(false));
  }, [id, result]);
  if (loading) {
    return <div className="app-shell"><SiteHeader /><main className="empty-state"><p>Lokales Profil wird geladen …</p></main></div>;
  }
  if (result === null) {
    return (
      <div className="app-shell">
        <SiteHeader />
        <main className="empty-state">
          <p className="eyebrow">PROFIL NICHT VERFÜGBAR</p>
          <h1>{message || "Dieser Atlas ist nicht lokal verfügbar."}</h1>
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
        <div className="local-actions">
          <button
            className="button button-quiet"
            type="button"
            onClick={() => {
              void localProfiles
                .saveProfile(result, true)
                .then(() => setMessage("Profil dauerhaft nur auf diesem Gerät gespeichert."))
                .catch((error: unknown) =>
                  setMessage(error instanceof Error ? error.message : "Speichern fehlgeschlagen."),
                );
            }}
          >
            Lokal speichern
          </button>
          {message && <p role="status">{message}</p>}
        </div>
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

function LibraryPage() {
  const [profiles, setProfiles] = useState<LocalProfile[]>([]);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<"name" | "updated">("updated");
  const [error, setError] = useState("");
  useEffect(() => {
    void localProfiles
      .listProfiles({ query, sort })
      .then(setProfiles)
      .catch((reason: unknown) =>
        setError(reason instanceof Error ? reason.message : "Bibliothek nicht verfügbar."),
      );
  }, [query, sort]);
  return (
    <div className="app-shell">
      <SiteHeader />
      <main className="library-page">
        <p className="eyebrow">NUR AUF DIESEM GERÄT</p>
        <h1>Deine Bibliothek</h1>
        <div className="library-tools">
          <label><span>Profile durchsuchen</span><input value={query} onChange={(event) => setQuery(event.target.value)} /></label>
          <label><span>Sortierung</span><select value={sort} onChange={(event) => setSort(event.target.value as "name" | "updated")}><option value="updated">Zuletzt geändert</option><option value="name">Name</option></select></label>
        </div>
        {error && <p className="notice notice-warning" role="alert">{error} <a href="/einstellungen">Tresor entsperren</a></p>}
        {!error && profiles.length === 0 && <p>Es sind noch keine Profile lokal gespeichert.</p>}
        <div className="library-grid">
          {profiles.map((profile) => (
            <article key={profile.id}>
              <p className="eyebrow">{profile.protected ? "GESCHÜTZT" : "LOKAL"}</p>
              <h2><a href={`/profil/${profile.id}`}>{profile.name}</a></h2>
              <small>{new Date(profile.updatedAt).toLocaleDateString("de-DE")}</small>
              <button type="button" className="expert-toggle" onClick={() => void localProfiles.deleteProfile(profile.id).then(() => setProfiles((current) => current.filter((item) => item.id !== profile.id)))}>Löschen</button>
            </article>
          ))}
        </div>
      </main>
    </div>
  );
}

function SettingsPage() {
  const [passphrase, setPassphrase] = useState("");
  const [message, setMessage] = useState("");
  const handle = (action: () => Promise<unknown>) => {
    void action().then(() => setMessage("Aktion erfolgreich.")).catch((error: unknown) => setMessage(error instanceof Error ? error.message : "Aktion fehlgeschlagen."));
  };
  const exportData = () =>
    handle(async () => {
      const archive = await localProfiles.exportAll(passphrase);
      const url = URL.createObjectURL(new Blob([JSON.stringify(archive)], { type: "application/json" }));
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `numra-export-${new Date().toISOString().slice(0, 10)}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
    });
  return (
    <div className="app-shell">
      <SiteHeader />
      <main className="settings-page">
        <p className="eyebrow">LOKALER DATENSCHUTZ</p><h1>Einstellungen</h1>
        <section className="settings-card">
          <h2>Passphraseschutz</h2>
          <p>Der Schlüssel bleibt ausschließlich im Arbeitsspeicher und wird nach 15 Minuten Inaktivität verworfen.</p>
          <label><span>Passphrase (mindestens 12 Zeichen)</span><input type="password" value={passphrase} onChange={(event) => setPassphrase(event.target.value)} /></label>
          <div className="hero-actions">
            <button className="button button-primary" type="button" onClick={() => handle(() => localProfiles.unlock(passphrase))}>Entsperren</button>
            <button className="button button-quiet" type="button" onClick={() => handle(() => localProfiles.enableProtection(passphrase))}>Für leere Bibliothek aktivieren</button>
            <button className="button button-quiet" type="button" onClick={() => { localProfiles.lock(); setMessage("Tresor gesperrt."); }}>Sperren</button>
          </div>
        </section>
        <section className="settings-card">
          <h2>Verschlüsselter Export und Import</h2>
          <p>Das Archiv enthält alle lokalen Numra-Daten und ist mit der oben eingegebenen Passphrase geschützt.</p>
          <div className="hero-actions">
            <button className="button button-quiet" type="button" onClick={exportData}>Archiv exportieren</button>
            <label className="button button-quiet file-button">Archiv importieren<input type="file" accept="application/json,.json" onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) handle(async () => {
                const parsed: unknown = JSON.parse(await file.text());
                await localProfiles.importAll(parseEncryptedArchive(parsed), passphrase);
              });
            }} /></label>
          </div>
        </section>
        <section className="settings-card danger-zone"><h2>Alle lokalen Daten löschen</h2><p>Diese Aktion entfernt Profile, Berechnungen, Berichte, Gespräche, Notizen und den Tresorschlüssel von diesem Gerät.</p><button className="button button-quiet" type="button" onClick={() => handle(() => localProfiles.deleteAllLocalData())}>Unwiderruflich lokal löschen</button></section>
        {message && <p role="status" className="notice">{message}</p>}
      </main>
    </div>
  );
}

export function App() {
  useEffect(() => {
    const activity = () => localProfiles.touch();
    const timer = window.setInterval(() => localProfiles.autoLockIfIdle(), 30_000);
    window.addEventListener("pointerdown", activity);
    window.addEventListener("keydown", activity);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("pointerdown", activity);
      window.removeEventListener("keydown", activity);
    };
  }, []);
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyse/neu" element={<NewAnalysisPage />} />
        <Route path="/profil/:id" element={<ProfilePage />} />
        <Route path="/bibliothek" element={<LibraryPage />} />
        <Route path="/einstellungen" element={<SettingsPage />} />
        <Route path="*" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  );
}
