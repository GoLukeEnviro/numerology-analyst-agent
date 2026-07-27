import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes, useNavigate, useParams } from "react-router-dom";

import type { ProfileCalculationResult } from "./api/types";
import { AnalysisWizard } from "./features/analysis/AnalysisWizard";
import { NumberAtlas, type AtlasNumber } from "./features/profile/NumberAtlas";
import { ProfileActions } from "./features/profile/ProfileActions";
import { ReportExperience } from "./features/report/ReportExperience";
import { PwaRegistration } from "./pwa/PwaUpdateNotice";
import { VaultLockedError, parseEncryptedArchive } from "./storage/crypto";
import { localProfiles, type LocalProfile } from "./storage/repository";
import { applyTheme, readTheme, type Theme } from "./theme";

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

function LegalFooter() {
  return (
    <footer className="legal-footer">
      <span>Numra · Symbolische Reflexion mit transparentem Rechenweg</span>
      <nav aria-label="Rechtliches">
        <a href="/datenschutz">Datenschutz</a>
        <a href="/impressum">Impressum</a>
        <a href="/nutzungsbedingungen">Nutzungsbedingungen</a>
      </nav>
    </footer>
  );
}

function InformationPage({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="app-shell">
      <SiteHeader />
      <main className="information-page">
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <div className="information-content">{children}</div>
      </main>
      <LegalFooter />
    </div>
  );
}

function KnowledgePage() {
  return (
    <InformationPage eyebrow="TRANSPARENTE METHODE" title="Methode und Aussagegrenzen">
      <section>
        <h2>Was Numra berechnet</h2>
        <p>
          Der deterministische Kern verwendet die pythagoreische
          Buchstaben-Zuordnung in der versionierten Policy v1. Er berechnet
          Lebensweg A und B, Geburtstag, Einstellung, Ausdruck,
          Seelenstreben, Persönlichkeit, Reife sowie persönliche Zyklen,
          Pinnacles und Challenges.
        </p>
        <p>
          Geburtsname und aktiver Name bleiben getrennt. Das explizite
          Berechnungsdatum, die Methodenpolicy und jeder Rechenschritt fließen
          in den reproduzierbaren Profilhash ein.
        </p>
      </section>
      <section>
        <h2>Vier Aussageklassen</h2>
        <dl className="information-list">
          <div><dt>Eingabefakt</dt><dd>Eine von dir bereitgestellte Angabe.</dd></div>
          <div><dt>Berechnungsfakt</dt><dd>Ein deterministisch reproduzierbares Ergebnis.</dd></div>
          <div><dt>Traditionelle Aussage</dt><dd>Überlieferte numerologische Symbolik.</dd></div>
          <div><dt>Interpretative Hypothese</dt><dd>Eine prüfbare Einladung zur persönlichen Reflexion.</dd></div>
        </dl>
      </section>
      <aside className="notice">
        <strong>Wissenschaftliche Grenze</strong>
        <p>
          Numerologie ist keine wissenschaftlich bestätigte Persönlichkeitsdiagnostik
          und ersetzt keine medizinische, psychologische, rechtliche oder
          finanzielle Beratung.
        </p>
      </aside>
    </InformationPage>
  );
}

function PrivacyPage() {
  return (
    <InformationPage eyebrow="DATENSCHUTZINFORMATION" title="Datenschutz">
      <section>
        <h2>Lokale Datenhoheit</h2>
        <p>
          Numra führt keine serverseitige Profilhistorie. Es gibt keine Konten
          oder Cloud-Synchronisierung. Dauerhaft gespeicherte Profile, Berichte,
          Rückfragen und Notizen liegen ausschließlich in der IndexedDB dieses
          Geräts und können optional mit einer Passphrase verschlüsselt werden.
        </p>
      </section>
      <section>
        <h2>Berechnung und Protokolle</h2>
        <p>
          Name, Geburtsdatum und Berechnungsdatum werden verschlüsselt per HTTPS
          zur flüchtigen Berechnung übertragen. Die API speichert weder
          Request-Body noch Ergebnis. Betriebslogs enthalten nur Methode, Pfad,
          Status, Korrelations-ID und Laufzeit – keine Namen, Geburtsdaten,
          Profilantworten oder KI-Ausgaben.
        </p>
      </section>
      <section>
        <h2>Optionale KI-Analyse</h2>
        <p>
          Erst nach separater Einwilligung erhält DeepSeek pseudonymisierte
          Berechnungsfakten und ausgewählte Wissensauszüge. Klarname und
          vollständiges Geburtsdatum werden nicht übertragen. Eine Verarbeitung
          in China ist möglich; die Funktion bleibt bis zur rechtlichen Prüfung
          des Drittlandtransfers standardmäßig deaktiviert.
        </p>
        <p>
          Für Missbrauchsschutz werden nur kurzlebige Redis-Zähler verwendet.
          Die IP-Adresse geht ausschließlich als HMAC-pseudonymisierter
          Tagesschlüssel ein und wird nicht im Klartext persistiert.
        </p>
      </section>
      <section>
        <h2>Deine Kontrolle</h2>
        <p>
          Unter Einstellungen kannst du alle lokalen Daten exportieren oder
          vollständig löschen. Da Numra keine serverseitigen Profile führt,
          kann der Betreiber verlorene lokale Daten oder Passphrasen nicht
          wiederherstellen.
        </p>
      </section>
    </InformationPage>
  );
}

function ImprintPage() {
  return (
    <InformationPage eyebrow="LAUNCH-GATE" title="Impressum">
      <aside className="notice notice-warning">
        <strong>Noch nicht öffentlich freigegeben</strong>
        <p>
          Numra bleibt für den öffentlichen Launch gesperrt, bis der Betreiber
          seine ladungsfähige Anschrift, Vertretungsangaben und eine
          Datenschutz-Kontaktadresse bereitgestellt und rechtlich geprüft hat.
        </p>
      </aside>
      <section>
        <h2>Warum hier keine Platzhalter stehen</h2>
        <p>
          Betreiberangaben sind Tatsachen und werden nicht erfunden. Das
          Deployment kann bis dahin ausschließlich als privates Staging
          betrieben werden.
        </p>
      </section>
      <section>
        <h2>Software</h2>
        <p>
          Der Quellcode von Numra steht unter der MIT-Lizenz. Lizenz und
          Haftungstext des Softwareprojekts bleiben davon unberührt.
        </p>
      </section>
    </InformationPage>
  );
}

function TermsPage() {
  return (
    <InformationPage eyebrow="NUTZUNGSRAHMEN" title="Nutzungsbedingungen">
      <section>
        <h2>Voraussetzungen</h2>
        <p>
          Numra richtet sich ausschließlich an Personen, die mindestens 18
          Jahre alt sind. Vor einer Berechnung ist die Altersbestätigung
          erforderlich.
        </p>
      </section>
      <section>
        <h2>Reflexion, nicht Diagnose</h2>
        <p>
          Ergebnisse und Berichte dienen der Unterhaltung und persönlichen
          Reflexion. Sie sind keine Tatsachenbehauptung über Persönlichkeit oder
          Zukunft und keine medizinische, psychologische, rechtliche oder
          finanzielle Beratung. Triff wichtige Entscheidungen nicht allein auf
          dieser Grundlage.
        </p>
      </section>
      <section>
        <h2>Lokale Verantwortung</h2>
        <p>
          Du entscheidest, ob Inhalte auf deinem Gerät gespeichert,
          verschlüsselt, exportiert oder gelöscht werden. Ohne Export gibt es
          keine serverseitige Wiederherstellung. Teile Berichte nur mit
          Einwilligung der betroffenen Person.
        </p>
      </section>
    </InformationPage>
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
  const selectedName = result.core_name ?? result.active_name;
  if (selectedName == null) {
    return (
      <div className="app-shell">
        <SiteHeader />
        <main className="empty-state">
          <h1>Das Profil enthält kein gültiges Namensprofil.</h1>
        </main>
      </div>
    );
  }
  const numbers: AtlasNumber[] = [
    { label: "Lebensweg", value: result.life_path_a.reduced_value, notation: result.life_path_a.compound_notation },
    { label: "Geburtstag", value: result.birthday.reduced_value, notation: result.birthday.compound_notation },
    { label: "Einstellung", value: result.attitude.reduced_value, notation: result.attitude.compound_notation },
    { label: "Ausdruck", value: selectedName.expression.reduced_value, notation: selectedName.expression.compound_notation },
    { label: "Seelenstreben", value: selectedName.soul_urge.reduced_value, notation: selectedName.soul_urge.compound_notation },
    { label: "Persönlichkeit", value: selectedName.personality.reduced_value, notation: selectedName.personality.compound_notation },
    { label: "Reife", value: result.maturity.reduced_value, notation: result.maturity.compound_notation },
    ...(result.core_name != null && result.active_name != null
      ? [
          { label: "Aktiver Ausdruck", value: result.active_name.expression.reduced_value, notation: result.active_name.expression.compound_notation },
          { label: "Aktives Seelenstreben", value: result.active_name.soul_urge.reduced_value, notation: result.active_name.soul_urge.compound_notation },
          { label: "Aktive Persönlichkeit", value: result.active_name.personality.reduced_value, notation: result.active_name.personality.compound_notation },
          { label: "Aktive Reife", value: result.active_name.maturity.reduced_value, notation: result.active_name.maturity.compound_notation },
        ]
      : []),
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
          <div className="profile-seal"><span>Schema</span><strong>V3</strong><small>verifiziert</small></div>
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
          <a className="button button-primary" href={`/profil/${id}/bericht`}>Reflexionsbericht</a>
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
        {id !== undefined && <ProfileActions profileId={id} profile={result} />}
      </main>
    </div>
  );
}

function ReportPage() {
  const { id } = useParams();
  const [profile, setProfile] = useState(() => readSessionProfile(id));
  const [message, setMessage] = useState("");
  useEffect(() => {
    if (profile !== null || id === undefined) return;
    void localProfiles
      .getProfile(id)
      .then((saved) => setProfile(saved?.profile ?? null))
      .catch((error: unknown) =>
        setMessage(error instanceof Error ? error.message : "Profil konnte nicht geladen werden."),
      );
  }, [id, profile]);
  return (
    <div className="app-shell">
      <SiteHeader />
      <main>
        {profile !== null && id !== undefined ? (
          <ReportExperience profile={profile} profileId={id} />
        ) : (
          <section className="empty-state">
            <p className="eyebrow">PROFIL ERFORDERLICH</p>
            <h1>{message || "Öffne oder speichere zuerst ein Profil."}</h1>
            <a className="button button-primary" href="/bibliothek">Zur Bibliothek</a>
          </section>
        )}
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
  const [theme, setTheme] = useState<Theme>(() => readTheme());
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
          <h2>Erscheinungsbild</h2>
          <p>Dark Atlas ist Standard. Deine manuelle Auswahl bleibt lokal gespeichert.</p>
          <div className="hero-actions" role="group" aria-label="Farbschema">
            {(["dark", "light"] as const).map((value) => (
              <button
                className={theme === value ? "button button-primary" : "button button-quiet"}
                type="button"
                key={value}
                onClick={() => {
                  applyTheme(value);
                  setTheme(value);
                }}
              >
                {value === "dark" ? "Dark Atlas" : "Light Atlas"}
              </button>
            ))}
          </div>
        </section>
        <section className="settings-card">
          <h2>Numra installieren</h2>
          <p><strong>Android und Desktop:</strong> Öffne das Browsermenü und wähle „App installieren“ oder „Zum Startbildschirm hinzufügen“.</p>
          <p><strong>iPhone und iPad:</strong> Öffne Numra in Safari, tippe auf „Teilen“ und anschließend auf „Zum Home-Bildschirm“.</p>
          <p>Die App-Oberfläche und lokal gespeicherte Profile bleiben offline lesbar. Neue Berechnungen und KI-Berichte benötigen eine Verbindung.</p>
        </section>
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
        <Route path="/profil/:id/bericht" element={<ReportPage />} />
        <Route path="/bibliothek" element={<LibraryPage />} />
        <Route path="/einstellungen" element={<SettingsPage />} />
        <Route path="/wissen" element={<KnowledgePage />} />
        <Route path="/datenschutz" element={<PrivacyPage />} />
        <Route path="/impressum" element={<ImprintPage />} />
        <Route path="/nutzungsbedingungen" element={<TermsPage />} />
        <Route path="*" element={<HomePage />} />
      </Routes>
      <PwaRegistration />
    </BrowserRouter>
  );
}
