import { lazy, Suspense, useState } from "react";

const ExpertDetails = lazy(() => import("./ExpertDetails"));

export interface AtlasNumber {
  label: string;
  value: number;
  notation: string;
}

interface NumberAtlasProps {
  hash: string;
  numbers: AtlasNumber[];
}

export function NumberAtlas({ hash, numbers }: NumberAtlasProps) {
  const [expert, setExpert] = useState(false);
  return (
    <section className="result-section" aria-labelledby="atlas-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">BERECHNETE KERNZAHLEN</p>
          <h2 id="atlas-title">Dein Zahlenatlas</h2>
        </div>
        <button className="expert-toggle" type="button" onClick={() => setExpert((value) => !value)}>
          {expert ? "Expertenansicht schließen" : "Expertenansicht öffnen"}
        </button>
      </div>
      <div className="number-grid">
        {numbers.map((number, index) => (
          <article className={index === 0 ? "number-card number-card-primary" : "number-card"} key={number.label}>
            <span className="claim-badge" aria-label="Aussageklasse Berechnung">Berechnung</span>
            <strong>{number.value}</strong>
            <h3>{number.label}</h3>
            {expert && <code>{number.notation}</code>}
          </article>
        ))}
      </div>
      <div className="table-scroll">
        <table aria-label="Tabellarischer Zahlenatlas">
          <thead><tr><th>Zahl</th><th>Wert</th><th>Rechenweg</th><th>Aussageklasse</th></tr></thead>
          <tbody>
            {numbers.map((number) => (
              <tr key={number.label}><td>{number.label}</td><td>{number.value}</td><td>{number.notation}</td><td>Berechnung</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      {expert && (
        <Suspense fallback={<p>Expertendaten werden geladen …</p>}>
          <ExpertDetails hash={hash} />
        </Suspense>
      )}
    </section>
  );
}
