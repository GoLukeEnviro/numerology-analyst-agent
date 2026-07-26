import { useEffect, useState } from "react";

import {
  generateFollowUp,
  generateReport,
} from "../../api/client";
import type {
  AnalysisFollowUp,
  AnalysisFollowUpRequest,
  AnalysisReport,
  AnalysisReportRequest,
  ProfileCalculationResult,
} from "../../api/types";
import { localProfiles } from "../../storage/repository";

const DEVICE_ID_KEY = "numra:device-id:v1";

function deviceId(): string {
  const existing = localStorage.getItem(DEVICE_ID_KEY);
  if (existing !== null) return existing;
  const created = `device-${crypto.randomUUID()}`;
  localStorage.setItem(DEVICE_ID_KEY, created);
  return created;
}

interface Quota {
  reports: number;
  followUps: number;
}

function quotaKey(hash: string): string {
  return `numra:llm-quota:v1:${hash}`;
}

function readQuota(hash: string): Quota {
  const value = localStorage.getItem(quotaKey(hash));
  if (value === null) return { reports: 0, followUps: 0 };
  try {
    return JSON.parse(value) as Quota;
  } catch {
    return { reports: 1, followUps: 2 };
  }
}

function writeQuota(hash: string, quota: Quota): void {
  localStorage.setItem(quotaKey(hash), JSON.stringify(quota));
}

interface ReportExperienceProps {
  profile: ProfileCalculationResult;
  profileId: string;
  requestReport?: (request: AnalysisReportRequest) => Promise<AnalysisReport>;
  requestFollowUp?: (request: AnalysisFollowUpRequest) => Promise<AnalysisFollowUp>;
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
  const [quota, setQuota] = useState(() => readQuota(profile.deterministic_hash));

  useEffect(() => {
    if (typeof indexedDB === "undefined") return;
    void Promise.all([
      localProfiles.getReport(profileId),
      localProfiles.listFollowUps(profileId),
    ])
      .then(([savedReport, savedFollowUps]) => {
        if (savedReport !== null) setReport(savedReport);
        setFollowUps(savedFollowUps);
      })
      .catch(() => setMessage("Lokale Analysedaten sind gesperrt oder nicht verfügbar."));
  }, [profileId]);

  const createReport = () => {
    if (!navigator.onLine) {
      setMessage("Für einen neuen Bericht ist eine Internetverbindung erforderlich.");
      return;
    }
    setBusy(true);
    setMessage("");
    void requestReport({
      consent: true,
      device_id: deviceId(),
      profile,
    })
      .then(async (created) => {
        setReport(created);
        const next = { ...quota, reports: 1 };
        setQuota(next);
        writeQuota(profile.deterministic_hash, next);
        if (saveLocally) await localProfiles.saveReport(profileId, created, true);
      })
      .catch((error: unknown) =>
        setMessage(error instanceof Error ? error.message : "Bericht konnte nicht erzeugt werden."),
      )
      .finally(() => setBusy(false));
  };

  const askFollowUp = () => {
    if (report === null || !question.trim()) return;
    if (!navigator.onLine) {
      setMessage("Für eine neue Rückfrage ist eine Internetverbindung erforderlich.");
      return;
    }
    setBusy(true);
    void requestFollowUp({
      consent: true,
      device_id: deviceId(),
      profile,
      report,
      question: question.trim(),
    })
      .then(async (created) => {
        setFollowUps((current) => [...current, created]);
        const next = { ...quota, followUps: quota.followUps + 1 };
        setQuota(next);
        writeQuota(profile.deterministic_hash, next);
        if (saveLocally) await localProfiles.saveFollowUp(profileId, created, true);
        setQuestion("");
      })
      .catch((error: unknown) =>
        setMessage(error instanceof Error ? error.message : "Rückfrage konnte nicht beantwortet werden."),
      )
      .finally(() => setBusy(false));
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
          <button className="button button-primary" type="button" disabled={!consent || busy || quota.reports >= 1} onClick={createReport}>
            {busy ? "Bericht wird geprüft …" : "Bericht erzeugen"}
          </button>
          {quota.reports >= 1 && <p>Das lokale Berichtskontingent für dieses Profil ist ausgeschöpft.</p>}
        </div>
      ) : (
        <div className="report-content">
          <p className="report-summary">{report.summary}</p>
          {report.sections.map((section) => (
            <article key={section.title}>
              <h2>{section.title}</h2>
              {section.claims.map((claim) => (
                <div className="report-claim" key={`${claim.calculation_ref}:${claim.text}`}>
                  <span className="claim-badge">{claim.claim_type.replaceAll("_", " ")}</span>
                  <p>{claim.text}</p>
                  <small>{claim.calculation_ref} · {claim.knowledge_ref}</small>
                </div>
              ))}
            </article>
          ))}
          <aside className="notice"><strong>Grenzen</strong>{report.limitations.map((item) => <p key={item}>{item}</p>)}</aside>
          <div className="follow-up-box">
            <h2>Rückfragen <small>{quota.followUps}/2</small></h2>
            {followUps.map((item, index) => <article key={`${item.provenance.prompt_tokens}:${index}`}><p>{item.answer}</p></article>)}
            <label><span>Deine Rückfrage</span><input maxLength={500} value={question} onChange={(event) => setQuestion(event.target.value)} /></label>
            <button className="button button-quiet" type="button" disabled={!consent || busy || !question.trim() || quota.followUps >= 2} onClick={askFollowUp}>Rückfrage senden</button>
          </div>
          <details><summary>Provenienz</summary><pre>{JSON.stringify(report.provenance, null, 2)}</pre></details>
        </div>
      )}
      {message && <p className="notice notice-warning" role="alert">{message}</p>}
    </section>
  );
}
