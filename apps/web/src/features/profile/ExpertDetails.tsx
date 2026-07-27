interface ExpertDetailsProps {
  hash: string;
  methodVersion: string;
  schemaVersion: string;
}

export default function ExpertDetails({
  hash,
  methodVersion,
  schemaVersion,
}: ExpertDetailsProps) {
  return (
    <div className="provenance">
      <span>Berechnungshash</span>
      <code>{hash}</code>
      <span>Schema</span>
      <code>{schemaVersion}</code>
      <span>Methode</span>
      <code>{methodVersion}</code>
    </div>
  );
}
