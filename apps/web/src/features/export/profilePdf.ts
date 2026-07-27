import * as pdfMake from "pdfmake/build/pdfmake";
import virtualFonts from "pdfmake/build/vfs_fonts";
import type { Content, TDocumentDefinitions } from "pdfmake/interfaces";

import type { AnalysisReport, ProfileCalculationResult } from "../../api/types";

pdfMake.addVirtualFileSystem(virtualFonts);

function numbers(profile: ProfileCalculationResult): Array<[string, number, string]> {
  const selectedName = profile.core_name ?? profile.active_name;
  if (selectedName == null) throw new Error("Profil ohne Namensprofil kann nicht exportiert werden.");
  const activeMaturity =
    profile.active_name != null && "maturity" in profile.active_name
      ? profile.active_name.maturity
      : undefined;
  return [
    ["Lebensweg", profile.life_path_a.reduced_value, profile.life_path_a.compound_notation],
    ["Geburtstag", profile.birthday.reduced_value, profile.birthday.compound_notation],
    ["Einstellung", profile.attitude.reduced_value, profile.attitude.compound_notation],
    ["Ausdruck", selectedName.expression.reduced_value, selectedName.expression.compound_notation],
    ["Seelenstreben", selectedName.soul_urge.reduced_value, selectedName.soul_urge.compound_notation],
    ["Persönlichkeit", selectedName.personality.reduced_value, selectedName.personality.compound_notation],
    ["Reife", profile.maturity.reduced_value, profile.maturity.compound_notation],
    ...(profile.core_name != null && profile.active_name != null
      ? [
          ["Aktiver Ausdruck", profile.active_name.expression.reduced_value, profile.active_name.expression.compound_notation] as [string, number, string],
          ["Aktives Seelenstreben", profile.active_name.soul_urge.reduced_value, profile.active_name.soul_urge.compound_notation] as [string, number, string],
          ["Aktive Persönlichkeit", profile.active_name.personality.reduced_value, profile.active_name.personality.compound_notation] as [string, number, string],
          ...(activeMaturity == null
            ? []
            : [["Aktive Reife", activeMaturity.reduced_value, activeMaturity.compound_notation] as [string, number, string]]),
        ]
      : []),
  ];
}

export function buildPdfLines(
  profile: ProfileCalculationResult,
  report: AnalysisReport | null,
): string[] {
  const lines = [
    "NUMRA - NUMEROLOGIE NACHVOLLZIEHBAR",
    profile.input_ref.core_name,
    `Stand: ${profile.input_ref.as_of_date}`,
    "Aussageklassen: Berechnung / Tradition / Hypothese / praktische Anregung",
    ...numbers(profile).map(([label, value, notation]) => `${label}: ${value} (${notation})`),
    `Persönliches Jahr: ${profile.cycles.personal_year.reduced_value}`,
    `Persönlicher Monat: ${profile.cycles.personal_month.reduced_value}`,
    `Persönlicher Tag: ${profile.cycles.personal_day.reduced_value}`,
    "Rechenweg",
    ...(profile.trace.calculation_steps ?? []).map(
      (step) =>
        `${step.label.replaceAll("_", " ")}: ${
          step.note || `${(step.inputs ?? []).join(" + ")} -> ${step.output}`
        }`,
    ),
    "Wissenschaftliche Grenze",
    "Numerologie ist keine wissenschaftlich validierte Persönlichkeitsdiagnostik, Diagnose oder Vorhersage.",
    `Berechnungshash: ${profile.deterministic_hash}`,
  ];
  if (report !== null) {
    lines.push("Validierter Reflexionsbericht", report.summary);
    for (const section of report.sections) {
      lines.push(section.title);
      for (const claim of section.claims) {
        lines.push(
          `[${claim.claim_type}] ${claim.text}`,
          `Referenzen: ${claim.calculation_ref} / ${claim.knowledge_ref}`,
        );
      }
    }
    lines.push(
      ...report.limitations,
      "Provenienz",
      `Provider: ${report.provenance.provider}`,
      `Modell: ${report.provenance.model}`,
      `Prompt: ${report.provenance.prompt_version}`,
      `Wissenspaket: ${report.provenance.knowledge_bundle}`,
    );
  }
  return lines;
}

export async function createProfilePdf(
  profile: ProfileCalculationResult,
  report: AnalysisReport | null,
): Promise<Uint8Array<ArrayBuffer>> {
  const numberRows = numbers(profile).map(([label, value, notation]) => [
    label,
    String(value),
    notation,
    "Berechnung",
  ]);
  const phaseRows = [
    ...profile.cycles.pinnacles.map((phase) => [
      `Pinnacle ${phase.ordinal}`,
      String(phase.number.reduced_value),
      `${phase.start_age}-${phase.end_age ?? "offen"}`,
    ]),
    ...profile.cycles.challenges.map((phase) => [
      `Challenge ${phase.ordinal}`,
      String(phase.number.reduced_value),
      `${phase.start_age}-${phase.end_age ?? "offen"}`,
    ]),
  ];
  const trace = (profile.trace.calculation_steps ?? []).map((step) => ({
    text: [
      { text: `${step.label.replaceAll("_", " ")}: `, bold: true },
      step.note || `${(step.inputs ?? []).join(" + ")} -> ${step.output}`,
    ],
    fontSize: 9,
    margin: [0, 0, 0, 3] as [number, number, number, number],
  }));
  const content: Content[] = [
    { text: "NUMRA - NUMEROLOGIE NACHVOLLZIEHBAR", style: "kicker" },
    { text: profile.input_ref.core_name, style: "title" },
    { text: `Stand ${profile.input_ref.as_of_date}`, color: "#607483", margin: [0, 0, 0, 22] },
    { text: "Zahlenatlas", style: "section" },
    {
      table: {
        headerRows: 1,
        widths: ["*", 45, 90, 75],
        body: [["Zahl", "Wert", "Notation", "Aussageklasse"], ...numberRows],
      },
      layout: "lightHorizontalLines",
      margin: [0, 0, 0, 20],
    },
    { text: "Persönliche Zyklen", style: "section" },
    {
      columns: [
        { text: `Jahr\n${profile.cycles.personal_year.reduced_value}`, style: "cycle" },
        { text: `Monat\n${profile.cycles.personal_month.reduced_value}`, style: "cycle" },
        { text: `Tag\n${profile.cycles.personal_day.reduced_value}`, style: "cycle" },
      ],
      columnGap: 10,
      margin: [0, 0, 0, 16],
    },
    {
      table: {
        headerRows: 1,
        widths: ["*", 60, 100],
        body: [["Phase", "Zahl", "Alter"], ...phaseRows],
      },
      layout: "lightHorizontalLines",
      margin: [0, 0, 0, 20],
    },
    {
      stack: [
        { text: "Aussageklassen", style: "section" },
        {
          text: "Berechnung / Tradition / Hypothese / praktische Anregung",
          margin: [0, 0, 0, 16],
        },
        {
          text: "Numerologie ist keine wissenschaftlich validierte Persönlichkeitsdiagnostik, Diagnose oder Vorhersage.",
          color: "#8a3d2f",
          fillColor: "#f8e9e4",
          margin: [10, 10, 10, 10],
        },
      ],
      pageBreak: "before",
      unbreakable: true,
    },
    { text: "Rechenweg", style: "section" },
    ...trace,
    { text: "Berechnungshash", style: "section" },
    { text: profile.deterministic_hash, fontSize: 8, color: "#607483" },
  ];
  if (report !== null) {
    const reportSections: Content[] = [];
    for (const section of report.sections) {
      reportSections.push({ text: section.title, style: "subsection" });
      for (const claim of section.claims) {
        reportSections.push({
          stack: [
            { text: claim.claim_type.replaceAll("_", " ").toUpperCase(), style: "badge" },
            { text: claim.text, margin: [0, 3, 0, 2] },
            {
              text: `${claim.calculation_ref} · ${claim.knowledge_ref}`,
              fontSize: 7,
              color: "#607483",
            },
          ],
          margin: [0, 0, 0, 12],
        });
      }
    }
    content.push(
      { text: "Validierter Reflexionsbericht", style: "section", pageBreak: "before" },
      { text: report.summary, style: "lead" },
      ...reportSections,
      { text: "Grenzen", style: "subsection" },
      { ul: report.limitations },
      { text: "Provenienz", style: "subsection" },
      {
        table: {
          widths: [110, "*"],
          body: [
            ["Provider", report.provenance.provider],
            ["Modell", report.provenance.model],
            ["Prompt", report.provenance.prompt_version],
            ["Wissenspaket", report.provenance.knowledge_bundle],
            ["Berechnungshash", report.provenance.calculation_hash],
          ],
        },
        layout: "lightHorizontalLines",
      },
    );
  }
  const definition: TDocumentDefinitions = {
    info: {
      title: `Numra Profil - ${profile.input_ref.core_name}`,
      author: "Numra",
      subject: "Nachvollziehbares numerologisches Profil",
    },
    pageSize: "A4",
    pageMargins: [54, 68, 54, 58],
    header: {
      text: "NUMRA · LOKAL ERZEUGTER EXPORT",
      color: "#237b78",
      fontSize: 8,
      margin: [54, 28, 54, 0],
    },
    footer: (currentPage, pageCount) => ({
      columns: [
        { text: profile.deterministic_hash.slice(0, 16), alignment: "left" },
        { text: `${currentPage} / ${pageCount}`, alignment: "right" },
      ],
      color: "#607483",
      fontSize: 8,
      margin: [54, 16, 54, 0],
    }),
    content,
    defaultStyle: {
      font: "Roboto",
      fontSize: 10,
      color: "#122536",
      lineHeight: 1.35,
    },
    styles: {
      kicker: {
        color: "#237b78",
        fontSize: 9,
        bold: true,
        characterSpacing: 1.3,
      },
      title: {
        color: "#07131e",
        fontSize: 28,
        bold: true,
      },
      section: {
        color: "#185d5b",
        fontSize: 16,
        bold: true,
        margin: [0, 14, 0, 8],
      },
      subsection: {
        color: "#122536",
        fontSize: 12,
        bold: true,
        margin: [0, 14, 0, 6],
      },
      lead: {
        color: "#40545f",
        fontSize: 13,
        lineHeight: 1.4,
        margin: [0, 0, 0, 14],
      },
      badge: {
        color: "#237b78",
        fontSize: 7,
        bold: true,
        characterSpacing: 0.7,
      },
      cycle: {
        alignment: "center",
        color: "#185d5b",
        fontSize: 15,
        bold: true,
        fillColor: "#e6f2ef",
        margin: [6, 10, 6, 10],
      },
    },
  };
  const buffer = await pdfMake.createPdf(definition).getBuffer();
  return Uint8Array.from(buffer);
}

export async function downloadProfilePdf(
  profile: ProfileCalculationResult,
  report: AnalysisReport | null,
): Promise<void> {
  const bytes = await createProfilePdf(profile, report);
  const blob = new Blob([bytes], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `numra-${profile.deterministic_hash.slice(0, 12)}.pdf`;
  anchor.click();
  URL.revokeObjectURL(url);
}
