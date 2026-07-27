import { useRegisterSW } from "virtual:pwa-register/react";

interface PwaUpdateNoticeProps {
  updateAvailable: boolean;
  onUpdate: (reloadPage?: boolean) => Promise<void>;
  onDismiss: () => void;
}

export function PwaUpdateNotice({
  updateAvailable,
  onUpdate,
  onDismiss,
}: PwaUpdateNoticeProps) {
  if (!updateAvailable) return null;
  return (
    <aside className="pwa-toast" role="status" aria-live="polite">
      <p><strong>Eine neue Numra-Version ist bereit.</strong></p>
      <div>
        <button className="button button-primary" type="button" onClick={() => void onUpdate(true)}>
          Jetzt aktualisieren
        </button>
        <button className="button button-quiet" type="button" onClick={onDismiss}>
          Später
        </button>
      </div>
    </aside>
  );
}

export function PwaRegistration() {
  const {
    needRefresh: [needRefresh, setNeedRefresh],
    offlineReady: [offlineReady, setOfflineReady],
    updateServiceWorker,
  } = useRegisterSW();
  return (
    <>
      <PwaUpdateNotice
        updateAvailable={needRefresh}
        onUpdate={updateServiceWorker}
        onDismiss={() => setNeedRefresh(false)}
      />
      {offlineReady && (
        <aside className="pwa-toast" role="status">
          <p>Numra ist für den Offline-Lesezugriff bereit.</p>
          <button className="button button-quiet" type="button" onClick={() => setOfflineReady(false)}>
            Schließen
          </button>
        </aside>
      )}
    </>
  );
}
