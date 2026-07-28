import { useEffect, useRef, useState } from "react";

import { ApiProblem, generateFollowUp, generateReport } from "../../api/client";
import type {
  AnalysisFollowUp,
  AnalysisReport,
  ProfileCalculationResult,
} from "../../api/types";
import { localProfiles } from "../../storage/repository";

const DEVICE_ID_KEY = "numra:device-id:v1";
const QUOTA_EXHAUSTED_CODES = new Set([
  "rate_limit_exceeded",
  "quota_exceeded",
  "daily_quota_exceeded",
]);

function deviceId(): string {
  const existing = localStorage.getItem(DEVICE_ID_KEY);
  if (existing !== null) return existing;
  const created = `device-${crypto.randomUUID()}`;
  localStorage.setItem(DEVICE_ID_KEY, created);
  return created;
}

function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === "AbortError";
}

function quotaExhaustedMessage(error: unknown): string | null {
  if (error instanceof ApiProblem && QUOTA_EXHAUSTED_CODES.has(error.code)) {
    return "Das tägliche Kontingent ist ausgeschöpft. Bitte versuche es morgen wieder.";
  }
  return null;
}

interface SectionNoteState {
  draft: string;
  saved: string | null;
}

interface ReportExperienceProps {
  profile: ProfileCalculationResult;
  profileId: string;
  requestReport?: typeof generateReport;
  requestFollowUp?: typeof generateFollowUp;
}

export function ReportExperience({
  profile,
  profileId,
  requestReport = generateReport,
  requestFollowUp = generateFollowUp,
}: ReportExperienceProps) {
  const [consent, setConsent] = useState(false);
  const [saveLocally, setSaveLocally] = useState(false);
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [followUps, setFollowUps] = useState<AnalysisFollowUp[]>([]);
  const [question, setQuestion] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [followUpCount, setFollowUpCount] = useState(0);
  const [sectionNotes, setSectionNotes] = useState<Record<string, SectionNoteState>>({});
  const [activeNoteSection, setActiveNoteSection] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (typeof indexedDB === "undefined") return;
    void Promise.all([
      localProfiles.getReport(profileId),
      localProfiles.listFollowUps(profileId),
    ])
      .then(async ([savedReport, savedFollowUps]) => {
        if (savedReport !== null) setReport(savedReport);
        setFollowUps(savedFollowUps);
        setFollowUpCount(savedFollowUps.length);
        if (savedReport !== null) {
          const notes: Record<string, SectionNoteState> = {};
          for (const section of savedReport.sections) {
            const saved = await localProfiles.getNote(profileId, section.title);
            notes[section.title] = { draft: "", saved };
          }
          setSectionNotes(notes);
        }
      })
      .catch(() => setMessage("Lokale Analysedaten sind gesperrt oder nicht verfügbar."));
    return () => {
      abortRef.current?.abort();
    };
  }, [profileId]);

  const startRequest = (): AbortController => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setBusy(true);
    setMessage("");
    return controller;
  };

  const finishRequest = () => {
    setBusy(false);
    if (abortRef.current?.signal.aborted) {
      abortRef.current = null;
    }
  };

  const createReport = () => {
    if (!navigator.onLine) {
      setMessage("Für einen neuen Bericht ist eine Internetverbindung erforderlich.");
      return;
    }
    const controller = startRequest();
    void requestReport(
      {
        consent: true,
        device_id: deviceId(),
        profile,
      },
      undefined,
      controller.signal,
    )
      .then(async (created) => {
        setReport(created);
        setFollowUpCount(0);
        if (saveLocally) await localProfiles.saveReport(profileId, created, true);
      })
      .catch((error: unknown) => {
        if (isAbortError(error)) return;
        setMessage(
          quotaExhaustedMessage(error) ??
            (error instanceof Error ? error.message : "Bericht konnte nicht erzeugt werden."),
        );
      })
      .finally(finishRequest);
  };

  const askFollowUp = () => {
    if (report === null || !question.trim()) return;
    if (!navigator.onLine) {
      setMessage("Für eine neue Rückfrage ist eine Internetverbindung erforderlich.");
      return;
    }
    const controller = startRequest();
    void requestFollowUp(
      {
        consent: true,
        device_id: deviceId(),
        profile,
        report,
        question: question.trim(),
      },
      undefined,
      controller.signal,
    )
      .then(async (created) => {
        setFollowUps((current) => [...current, created]);
        setFollowUpCount((current) => current + 1);
        if (saveLocally) await localProfiles.saveFollowUp(profileId, created, true);
        setQuestion("");
      })
      .catch((error: unknown) => {
        if (isAbortError(error)) return;
        setMessage(
          quotaExhaustedMessage(error) ??
            (error instanceof Error ? error.message : "Rückfrage konnte nicht beantwortet werden."),
        );
      })
      .finally(finishRequest);
  };

  const cancelRequest = () => {
    abortRef.current?.abort();
    abortRef.current = null;
    setBusy(false);
  };

  const saveSectionNote = async (sectionTitle: string) => {
    const draft = sectionNotes[sectionTitle]?.draft.trim() ?? "";
    if (!draft) return;
    try {
      await localProfiles.saveNote(profileId, draft, true, sectionTitle);
      setSectionNotes((current) => ({
        ...current,
        [sectionTitle]: { draft: "", saved: draft },
      }));
      setActiveNoteSection((current) => (current === sectionTitle ? null : current));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Notiz konnte nicht gespeichert werden.");
    }
  };

  return (
    <section className="report-experience">
      <header>
        <p className="eyebrow">OPTIONALE KI-ANALYSE</p>
        <h1>Dein Reflexionsbericht</h1>
        <p>Berechnete Werte bleiben unverändert und werden vor jeder Anzeige validiert.</p>
      </header>
      {report === null ? (
        <div className="provider-consent">
          <h2>Datenschutzgrenze vor der Übertragung</h2>
          <dl>
            <div><dt>Anbieter</dt><dd>DeepSeek</dd></div>
            <div><dt>Übertragen</dt><dd>Berechnungsfakten, Profilhash, Aussageklassen und notwendige Wissensauszüge</dd></div>
            <div><dt>Nicht übertragen</dt><dd>Weder Klarname noch vollständiges Geburtsdatum</dd></div>
            <div><dt>Verarbeitung</dt><dd>Externer Anbieter; mögliche Verarbeitung in China. Drittlandtransfer muss der Betreiber vor Freischaltung rechtlich prüfen.</dd></div>
          </dl>
          <label className="check-row">
            <input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} />
            <span>Ich willige ausdrücklich in diese Übertragung ein.</span>
          </label>
          <label className="check-row">
            <input type="checkbox" checked={saveLocally} onChange={(event) => setSaveLocally(event.target.checked)} />
            <span>Bericht und Rückfragen dauerhaft auf diesem Gerät speichern.</span>
          </label>
          <div className="hero-actions">
            <button className="button button-primary" type="button" disabled={!consent || busy} onClick={createReport}>
              {busy ? "Bericht wird geprüft …" : "Bericht erzeugen"}
            </button>
            {busy && (
              <button className="button button-quiet" type="button" onClick={cancelRequest}>
                Abbrechen
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="report-content">
          <p className="report-summary">{report.summary}</p>
          {report.sections.map((section) => {
            const noteState = sectionNotes[section.title];
            return (
              <article key={section.title}>
                <h2>{section.title}</h2>
                {section.claims.map((claim) => (
                  <div className="report-claim" key={`${claim.calculation_ref}:${claim.text}`}>
                    <span className="claim-badge">{claim.claim_type.replaceAll("_", " ")}</span>
                    <p>{claim.text}</p>
                    <small>{claim.calculation_ref} · {claim.knowledge_ref}</small>
                  </div>
                ))}
                <div className="section-note">
                  {noteState?.saved && <p className="section-note-saved">{noteState.saved}</p>}
                  {activeNoteSection === section.title ? (
                    <div className="section-note-form">
                      <label className="visually-hidden" htmlFor={`note-${section.title}`}>
                        Notiz zu {section.title}
                      </label>
                      <textarea
                        id={`note-${section.title}`}
                        className="section-note-input"
                        maxLength={5_000}
                        value={noteState?.draft ?? ""}
                        onChange={(event) =>
                          setSectionNotes((current) => ({
                            ...current,
                            [section.title]: { draft: event.target.value, saved: noteState?.saved ?? null },
                          }))
                        }
                        placeholder="Notiz bleibt ausschließlich lokal auf diesem Gerät."
                      />
                      <div className="hero-actions">
                        <button
                          className="button button-quiet"
                          type="button"
                          disabled={noteState === undefined || noteState.draft.trim() === ""}
                          onClick={() => void saveSectionNote(section.title)}
                        >
                          Notiz speichern
                        </button>
                        <button
                          className="button button-quiet"
                          type="button"
                          onClick={() => setActiveNoteSection(null)}
                        >
                          Schließen
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      className="button button-quiet section-note-toggle"
                      type="button"
                      onClick={() => setActiveNoteSection(section.title)}
                    >
                      Notiz hinzufügen
                    </button>
                  )}
                </div>
              </article>
            );
          })}
          <aside className="notice"><strong>Grenzen</strong>{report.limitations.map((item) => <p key={item}>{item}</p>)}</aside>
          <div className="follow-up-box">
            <h2>Rückfragen <small>{followUpCount}/2</small></h2>
            {followUps.map((item, index) => <article key={`${item.provenance.prompt_tokens}:${index}`}><p>{item.answer}</p></article>)}
            <p>
              Der Rückfragetext wird an DeepSeek übertragen. Erkennbare
              Namensbestandteile aus diesem Profil und übliche vollständige
              Datumsformen werden serverseitig abgewiesen. Gib keine weiteren
              personenbezogenen Angaben ein.
            </p>
            <label className="check-row">
              <input
                type="checkbox"
                checked={consent}
                onChange={(event) => setConsent(event.target.checked)}
              />
              <span>Ich willige ein, diese Rückfrage ohne personenbezogene Daten zu übertragen.</span>
            </label>
            <label><span>Deine Rückfrage</span><input maxLength={500} value={question} onChange={(event) => setQuestion(event.target.value)} /></label>
            <div className="hero-actions">
              <button className="button button-quiet" type="button" disabled={!consent || busy || !question.trim() || followUpCount >= 2} onClick={askFollowUp}>Rückfrage senden</button>
              {busy && (
                <button className="button button-quiet" type="button" onClick={cancelRequest}>
                  Abbrechen
                </button>
              )}
            </div>
          </div>
          <details><summary>Provenienz</summary><pre>{JSON.stringify(report.provenance, null, 2)}</pre></details>
        </div>
      )}
      {message && <p className="notice notice-warning" role="alert">{message}</p>}
    </section>
  );
}
