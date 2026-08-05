/**
 * Profile presentation model — stable, version-independent adapter.
 *
 * Maps both V1/V3 ``ProfileCalculationResult`` and V4
 * ``ProfileCalculationResultV4`` onto a unified ``ProfilePresentationModel``
 * consumed by ``ResultsTabs``, ``NumberAtlas``, ``ProfileActions``,
 * PDF export and the library view.
 */
import type { ProfileCalculationResult } from "../../api/types";

export interface AtlasNumber {
    label: string;
    value: string;
    notation: string;
    isMaster: boolean;
    rootValue: number;
    heldMasterValue: number | null;
}

export interface ProfilePresentationModel {
    name: string;
    birthDate: string;
    methodVersion: string;
    schemaVersion: string;
    calculationHash: string;
    atlasNumbers: AtlasNumber[];
    pinnacles: { label: string; notation: string; rootValue: number }[];
    challenges: { label: string; value: number }[];
    personalYear: { notation: string; rootValue: number } | null;
    personalMonth: { notation: string; rootValue: number } | null;
    personalDay: { notation: string; rootValue: number } | null;
}

function extractNumberModel(nm: Record<string, unknown> | undefined): {
    display: string;
    root: number;
    held: number | null;
    isMaster: boolean;
} {
    if (!nm) return { display: "—", root: 0, held: null, isMaster: false };
    return {
        display:
            (nm.display_notation as string) ||
            String(nm.root_value ?? nm.reduced_value ?? "—"),
        root: (nm.root_value as number) ?? (nm.reduced_value as number) ?? 0,
        held: (nm.held_master_value as number) ?? null,
        isMaster: (nm.is_master as boolean) ?? false,
    };
}

export function toProfilePresentationModel(
    profile: ProfileCalculationResult | Record<string, unknown>,
): ProfilePresentationModel {
    const p = profile as Record<string, unknown>;
    const inputRef = (p.input_ref ?? p) as Record<string, unknown>;

    const lifePathPrimary = extractNumberModel(
        p.life_path_primary as Record<string, unknown>,
    );
    const lifePathSecondary = extractNumberModel(
        p.life_path_secondary as Record<string, unknown>,
    );
    const birthday = extractNumberModel(p.birthday as Record<string, unknown>);
    const attitude = extractNumberModel(p.attitude as Record<string, unknown>);
    const maturity = extractNumberModel(p.maturity as Record<string, unknown>);

    const coreName = (p.core_name ?? {}) as Record<string, unknown>;
    const expression = extractNumberModel(
        coreName.expression as Record<string, unknown>,
    );
    const soulUrge = extractNumberModel(
        coreName.soul_urge as Record<string, unknown>,
    );
    const personality = extractNumberModel(
        coreName.personality as Record<string, unknown>,
    );

    const cycles = (p.cycles ?? {}) as Record<string, unknown>;
    const personalYear = extractNumberModel(
        cycles.personal_year as Record<string, unknown>,
    );
    const personalMonth = extractNumberModel(
        cycles.personal_month as Record<string, unknown>,
    );
    const personalDay = extractNumberModel(
        cycles.personal_day as Record<string, unknown>,
    );

    const atlasNumbers: AtlasNumber[] = [
        {
            label: "Lebensweg (primär)",
            value: `LP1:${lifePathPrimary.display}`,
            notation: lifePathPrimary.display,
            isMaster: lifePathPrimary.isMaster,
            rootValue: lifePathPrimary.root,
            heldMasterValue: lifePathPrimary.held,
        },
        {
            label: "Lebensweg (sekundär)",
            value: `LP2:${lifePathSecondary.display}`,
            notation: lifePathSecondary.display,
            isMaster: lifePathSecondary.isMaster,
            rootValue: lifePathSecondary.root,
            heldMasterValue: lifePathSecondary.held,
        },
        {
            label: "Geburtstag",
            value: `BD:${birthday.display}`,
            notation: birthday.display,
            isMaster: birthday.isMaster,
            rootValue: birthday.root,
            heldMasterValue: birthday.held,
        },
        {
            label: "Einstellung",
            value: `AT:${attitude.display}`,
            notation: attitude.display,
            isMaster: attitude.isMaster,
            rootValue: attitude.root,
            heldMasterValue: attitude.held,
        },
        {
            label: "Ausdruck",
            value: `EX:${expression.display}`,
            notation: expression.display,
            isMaster: expression.isMaster,
            rootValue: expression.root,
            heldMasterValue: expression.held,
        },
        {
            label: "Seelenstreben",
            value: `SU:${soulUrge.display}`,
            notation: soulUrge.display,
            isMaster: soulUrge.isMaster,
            rootValue: soulUrge.root,
            heldMasterValue: soulUrge.held,
        },
        {
            label: "Persönlichkeit",
            value: `PE:${personality.display}`,
            notation: personality.display,
            isMaster: personality.isMaster,
            rootValue: personality.root,
            heldMasterValue: personality.held,
        },
        {
            label: "Reife",
            value: `MA:${maturity.display}`,
            notation: maturity.display,
            isMaster: maturity.isMaster,
            rootValue: maturity.root,
            heldMasterValue: maturity.held,
        },
    ];

    const pinnacleList = (p.pinnacles as Array<Record<string, unknown>>) ?? [];
    const challengeList =
        (p.challenges as Array<number | Record<string, unknown>>) ?? [];
    const pinnacles = pinnacleList.map((pn, i) => ({
        label: `Pinnacle ${i + 1}`,
        notation: extractNumberModel(pn).display,
        rootValue: extractNumberModel(pn).root,
    }));
    const challenges = challengeList.map((ch, i) => ({
        label: `Challenge ${i + 1}`,
        value:
            typeof ch === "number"
                ? ch
                : (((ch as Record<string, unknown>).reduced_value as number) ??
                  0),
    }));

    return {
        name: (inputRef.core_name as string) || (inputRef.name as string) || "",
        birthDate: (inputRef.birth_date as string) || "",
        methodVersion:
            ((p.policy as Record<string, unknown>)?.version as string) ||
            (p.method_version as string) ||
            "",
        schemaVersion: (p.schema_version as string) || "",
        calculationHash: (p.deterministic_hash as string) || "",
        atlasNumbers,
        pinnacles,
        challenges,
        personalYear:
            personalYear.root > 0
                ? {
                      notation: personalYear.display,
                      rootValue: personalYear.root,
                  }
                : null,
        personalMonth:
            personalMonth.root > 0
                ? {
                      notation: personalMonth.display,
                      rootValue: personalMonth.root,
                  }
                : null,
        personalDay:
            personalDay.root > 0
                ? { notation: personalDay.display, rootValue: personalDay.root }
                : null,
    };
}
