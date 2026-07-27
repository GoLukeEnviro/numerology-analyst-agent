interface ExpertDetailsProps {
  hash: string;
}

export default function ExpertDetails({ hash }: ExpertDetailsProps) {
  return (
    <div className="provenance">
      <span>Berechnungshash</span>
      <code>{hash}</code>
      <span>Schema</span>
      <code>profile-calculation-result-v3</code>
      <span>Methode</span>
      <code>pythagorean-v1</code>
    </div>
  );
}
