import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ApiProblem, calculateProfile } from "../../api/client";
import type {
    ProfileCalculationRequest,
    ProfileCalculationResult,
} from "../../api/types";
import { isAbortError } from "./abort-utils";

const formSchema = z
    .object({
        coreName: z
            .string()
            .trim()
            .min(1, "Bitte gib deinen Geburtsnamen ein.")
            .max(200),
        activeName: z.string().trim().max(200),
        birthDate: z.iso.date(),
        asOfDate: z.iso.date(),
        ageConfirmed: z.boolean(),
    })
    .superRefine((value, context) => {
        if (!value.ageConfirmed) {
            context.addIssue({
                code: "custom",
                path: ["ageConfirmed"],
                message: "Numra ist ausschließlich für Erwachsene.",
            });
        }
        if (value.birthDate > value.asOfDate) {
            context.addIssue({
                code: "custom",
                path: ["birthDate"],
                message:
                    "Das Geburtsdatum darf nicht nach dem Berechnungsdatum liegen.",
            });
        }
    });

type FormValues = z.infer<typeof formSchema>;
type Calculate = typeof calculateProfile;

interface AnalysisWizardProps {
    calculate?: Calculate;
    onComplete: (result: ProfileCalculationResult) => void;
    online?: boolean;
    methodVersion?: "v1" | "v2";
}

const defaultValues: FormValues = {
    coreName: "",
    activeName: "",
    birthDate: "",
    asOfDate: "",
    ageConfirmed: false,
};

function toRequest(
    values: FormValues,
    methodVersion: "v1" | "v2" = "v1",
): ProfileCalculationRequest {
    return {
        person: {
            core_name: values.coreName,
            active_name: values.activeName || null,
            birth_date: values.birthDate,
            as_of_date: values.asOfDate,
            locale: "de",
            consent_given: false,
        },
        policy: {
            system: "pythagorean",
            version: methodVersion,
            y_mode: "phonetic",
            umlaut_policy: "de-direct-v1",
            name_basis: "both_separate",
            date_method: "both",
            locale: "de",
            master_numbers: [11, 22, 33],
        },
    };
}

export function AnalysisWizard({
    calculate = calculateProfile,
    onComplete,
    online = navigator.onLine,
    methodVersion = "v1",
}: AnalysisWizardProps) {
    const [step, setStep] = useState<1 | 2>(1);
    const [review, setReview] = useState<FormValues | null>(null);
    const [methodAccepted, setMethodAccepted] = useState(false);
    const [pending, setPending] = useState(false);
    const [apiError, setApiError] = useState("");
    const abortRef = useRef<AbortController | null>(null);
    useEffect(() => () => abortRef.current?.abort(), []);
    const {
        register,
        handleSubmit,
        setError,
        formState: { errors },
    } = useForm<FormValues>({ defaultValues });

    const reviewValues = handleSubmit((values) => {
        const parsed = formSchema.safeParse(values);
        if (!parsed.success) {
            for (const issue of parsed.error.issues) {
                const field = issue.path[0];
                if (typeof field === "string" && field in values) {
                    setError(field as keyof FormValues, {
                        message: issue.message,
                    });
                }
            }
            return;
        }
        setReview(parsed.data);
        setStep(2);
    });

    const submit = async () => {
        if (review === null || !methodAccepted || !online) return;
        abortRef.current?.abort();
        const controller = new AbortController();
        abortRef.current = controller;
        setPending(true);
        setApiError("");
        try {
            const result = await calculate(
                toRequest(review, methodVersion),
                undefined,
                controller.signal,
            );
            if (abortRef.current !== controller) return;
            onComplete(result);
        } catch (error) {
            if (isAbortError(error)) return;
            if (abortRef.current !== controller) return;
            setApiError(
                error instanceof ApiProblem
                    ? `${error.message} Referenz: ${error.correlationId}`
                    : "Die Berechnung ist gerade nicht erreichbar. Bitte versuche es erneut.",
            );
        } finally {
            if (abortRef.current === controller) {
                abortRef.current = null;
                setPending(false);
            }
        }
    };

    const cancelCalculation = () => {
        abortRef.current?.abort();
        abortRef.current = null;
        setPending(false);
    };

    return (
        <section className="analysis-layout">
            <aside className="step-rail" aria-label="Fortschritt">
                <p className="eyebrow">NEUES PROFIL</p>
                <ol>
                    <li className={step === 1 ? "active" : "complete"}>
                        <span>01</span>Daten
                    </li>
                    <li className={step === 2 ? "active" : ""}>
                        <span>02</span>Prüfung
                    </li>
                    <li>
                        <span>03</span>Atlas
                    </li>
                </ol>
                <p>
                    Deine Eingaben werden für die Berechnung übertragen, aber
                    nicht serverseitig gespeichert.
                </p>
            </aside>

            <div className="analysis-panel">
                {step === 1 ? (
                    <>
                        <p className="eyebrow">SCHRITT 1 VON 3</p>
                        <h1>Deine Ausgangsdaten</h1>
                        <p className="panel-lead">
                            Der Geburtsname bildet das Kernprofil. Ein aktiver
                            Name bleibt davon vollständig getrennt.
                        </p>
                        {!online && (
                            <div className="notice notice-warning">
                                Offline keine neue Berechnung möglich.
                                Gespeicherte Profile bleiben später lesbar.
                            </div>
                        )}
                        <form
                            onSubmit={(event) => {
                                void reviewValues(event);
                            }}
                            className="analysis-form"
                            noValidate
                        >
                            <label>
                                <span>Vollständiger Geburtsname</span>
                                <input
                                    autoComplete="name"
                                    {...register("coreName")}
                                />
                                {errors.coreName && (
                                    <small role="alert">
                                        {errors.coreName.message}
                                    </small>
                                )}
                            </label>
                            <label>
                                <span>
                                    Aktuell verwendeter Name <em>optional</em>
                                </span>
                                <input
                                    autoComplete="off"
                                    {...register("activeName")}
                                />
                            </label>
                            <div className="field-pair">
                                <label>
                                    <span>Geburtsdatum</span>
                                    <input
                                        type="date"
                                        {...register("birthDate")}
                                    />
                                    {errors.birthDate && (
                                        <small role="alert">
                                            {errors.birthDate.message}
                                        </small>
                                    )}
                                </label>
                                <label>
                                    <span>Berechnungsdatum</span>
                                    <input
                                        type="date"
                                        {...register("asOfDate")}
                                    />
                                </label>
                            </div>
                            <label className="check-row">
                                <input
                                    type="checkbox"
                                    {...register("ageConfirmed")}
                                />
                                <span>Ich bin mindestens 18 Jahre alt.</span>
                            </label>
                            {errors.ageConfirmed && (
                                <small role="alert">
                                    {errors.ageConfirmed.message}
                                </small>
                            )}
                            <button
                                className="button button-primary"
                                type="submit"
                                disabled={!online}
                            >
                                Eingaben prüfen
                            </button>
                        </form>
                    </>
                ) : (
                    <>
                        <p className="eyebrow">SCHRITT 2 VON 3</p>
                        <h1>Prüfen und freigeben</h1>
                        <p className="panel-lead">
                            Kontrolliere die Daten. Die Methodenpolicy ist fest
                            und wird mit dem Ergebnis versioniert.
                        </p>
                        <dl className="review-grid">
                            <div>
                                <dt>Geburtsname</dt>
                                <dd>{review?.coreName}</dd>
                            </div>
                            <div>
                                <dt>Aktiver Name</dt>
                                <dd>
                                    {review?.activeName || "Nicht angegeben"}
                                </dd>
                            </div>
                            <div>
                                <dt>Geboren</dt>
                                <dd>{review?.birthDate}</dd>
                            </div>
                            <div>
                                <dt>Stand</dt>
                                <dd>{review?.asOfDate}</dd>
                            </div>
                        </dl>
                        <div className="method-stamp">
                            <span>PYTHAGOREAN · V1</span>
                            <strong>
                                Deterministisch · Meisterzahlen 11 / 22 / 33
                            </strong>
                        </div>
                        <label className="check-row consent-row">
                            <input
                                type="checkbox"
                                checked={methodAccepted}
                                onChange={(event) =>
                                    setMethodAccepted(event.target.checked)
                                }
                            />
                            <span>
                                Ich verstehe, dass Numerologie eine symbolische
                                Reflexionsmethode und keine wissenschaftliche
                                Diagnose ist.
                            </span>
                        </label>
                        {apiError && (
                            <div className="notice notice-error" role="alert">
                                {apiError}
                            </div>
                        )}
                        <div className="wizard-actions">
                            <button
                                className="button button-quiet"
                                type="button"
                                onClick={() => setStep(1)}
                            >
                                Zurück
                            </button>
                            <button
                                className="button button-primary"
                                type="button"
                                disabled={!methodAccepted || pending || !online}
                                onClick={() => void submit()}
                            >
                                {pending
                                    ? "Atlas wird berechnet …"
                                    : "Profil berechnen"}
                            </button>
                            {pending && (
                                <button
                                    className="button button-quiet"
                                    type="button"
                                    onClick={cancelCalculation}
                                >
                                    Abbrechen
                                </button>
                            )}
                        </div>
                    </>
                )}
            </div>
        </section>
    );
}
