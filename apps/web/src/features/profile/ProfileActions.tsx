import { useEffect, useState } from "react";

import type { ProfileCalculationResult } from "../../api/types";
import { noteErrorMessage } from "../analysis/notes-utils";
import { localProfiles } from "../../storage/repository";

interface ProfileActionsProps {
  profileId: string;
  profile: ProfileCalculationResult;
}

export function ProfileActions({ profileId, profile }: ProfileActionsProps) {
  const [note, setNote] = useState("");
  const [message, setMessage] = useState("");
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (typeof indexedDB === "undefined") return;
    void localProfiles
      .getNote(profileId)
      .then((saved) => setNote(saved ?? ""))
      .catch(() => setMessage("Notiz ist gesperrt oder nicht verfügbar."));
  }, [profileId]);

  const exportPdf = () => {
    setExporting(true);
    void Promise.all([
      import("../export/profilePdf"),
      localProfiles.getReport(profileId).catch(() => null),
    ])
      .then(([module, report]) => module.downloadProfilePdf(profile, report))
      .catch((error: unknown) =>
        setMessage(error instanceof Error ? error.message : "PDF-Export fehlgeschlagen."),
      )
      .finally(() => setExporting(false));
  };

  return (
    <section className="profile-tools result-section">
      <div>
        <p className="eyebrow">DEIN ARBEITSRAUM</p>
        <h2>Notiz und Export</h2>
      </div>
      <label>
        <span>Private Notiz auf diesem Gerät</span>
        <textarea
          maxLength={5_000}
          rows={6}
          value={note}
          onChange={(event) => setNote(event.target.value)}
        />
      </label>
      <div className="hero-actions">
        <button
          className="button button-quiet"
          type="button"
          disabled={!note.trim()}
          onClick={() => {
            void localProfiles
              .saveNote(profileId, note, true)
              .then(() => setMessage("Notiz lokal gespeichert."))
              .catch((error: unknown) => setMessage(noteErrorMessage(error)));
          }}
        >
          Notiz lokal speichern
        </button>
        <button
          className="button button-quiet"
          type="button"
          onClick={() => {
            void localProfiles.deleteNote(profileId).then(() => {
              setNote("");
              setMessage("Notiz gelöscht.");
            });
          }}
        >
          Notiz löschen
        </button>
        <button className="button button-primary" type="button" disabled={exporting} onClick={exportPdf}>
          {exporting ? "PDF wird erstellt …" : "PDF exportieren"}
        </button>
      </div>
      {message && <p role="status">{message}</p>}
    </section>
  );
}
