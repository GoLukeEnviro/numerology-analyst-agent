import { describe, expect, it } from "vitest";

import { toProfilePresentationModel } from "./presentation";

/**
 * Presentation adapter tests — V1/V3 (NumberResult) and V4 (NumberModel)
 * profiles must map onto the unified presentation model without silent
 * fallbacks or wrong values.
 */

function numberModel(overrides: Record<string, unknown> = {}) {
    return {
        raw_total: 40,
        root_value: 4,
        reduction_chain: [40, 4],
        display_notation: "40/4",
        is_master: false,
        held_master_value: null,
        karmic_occurrences: [],
        ...overrides,
    };
}

function v4Profile() {
    return {
        schema_version: "profile-calculation-result-v4",
        deterministic_hash: "a".repeat(64),
        name: "complete_profile_v4",
        input_ref: {
            core_name: "Lukas Springer",
            birth_date: "1986-07-18",
            as_of_date: "2026-01-01",
        },
        policy: { system: "pythagorean", version: "v2" },
        life_path_primary: numberModel({
            raw_total: 40,
            root_value: 4,
            reduction_chain: [40, 4],
            display_notation: "40/4",
        }),
        life_path_secondary: numberModel({
            raw_total: 22,
            root_value: 4,
            reduction_chain: [22, 4],
            display_notation: "22/4",
            is_master: true,
            held_master_value: 22,
        }),
        birthday: numberModel({
            raw_total: 18,
            root_value: 9,
            reduction_chain: [18, 9],
            display_notation: "18/9",
        }),
        attitude: numberModel({
            raw_total: 25,
            root_value: 7,
            reduction_chain: [25, 7],
            display_notation: "25/7",
        }),
        core_name: {
            basis: "core_name",
            expression: numberModel({
                raw_total: 62,
                root_value: 8,
                reduction_chain: [62, 8],
                display_notation: "62/8",
            }),
            soul_urge: numberModel({
                raw_total: 18,
                root_value: 9,
                reduction_chain: [18, 9],
                display_notation: "18/9",
            }),
            personality: numberModel({
                raw_total: 44,
                root_value: 8,
                reduction_chain: [44, 8],
                display_notation: "44/8",
                is_master: false,
            }),
        },
        cycles: {
            as_of_date: "2026-01-01",
            personal_year: numberModel({
                raw_total: 17,
                root_value: 8,
                reduction_chain: [17, 8],
                display_notation: "17/8",
            }),
            personal_month: numberModel({
                raw_total: 1,
                root_value: 1,
                reduction_chain: [1],
                display_notation: "1",
            }),
            personal_day: numberModel({
                raw_total: 9,
                root_value: 9,
                reduction_chain: [9],
                display_notation: "9",
            }),
            pinnacles: [
                numberModel({ raw_total: 16, root_value: 7, display_notation: "16/7" }),
                numberModel({ raw_total: 15, root_value: 6, display_notation: "15/6" }),
                numberModel({ raw_total: 13, root_value: 4, display_notation: "13/4" }),
                numberModel({ raw_total: 13, root_value: 4, display_notation: "13/4" }),
            ],
            challenges: [
                numberModel({ raw_total: 2, root_value: 2, display_notation: "2" }),
                numberModel({ raw_total: 3, root_value: 3, display_notation: "3" }),
                numberModel({ raw_total: 1, root_value: 1, display_notation: "1" }),
                numberModel({ raw_total: 1, root_value: 1, display_notation: "1" }),
            ],
        },
    };
}

describe("toProfilePresentationModel (V4)", () => {
    it("maps all expected fields from a canonical V4 profile", () => {
        const model = toProfilePresentationModel(v4Profile());

        expect(model.name).toBe("Lukas Springer");
        expect(model.birthDate).toBe("1986-07-18");
        expect(model.methodVersion).toBe("v2");
        expect(model.schemaVersion).toBe("profile-calculation-result-v4");
        expect(model.calculationHash).toBe("a".repeat(64));
    });

    it("keeps primary and secondary life path separate with master flags", () => {
        const model = toProfilePresentationModel(v4Profile());
        const lp1 = model.atlasNumbers.find((n) => n.label === "Lebensweg (primär)");
        const lp2 = model.atlasNumbers.find((n) => n.label === "Lebensweg (sekundär)");

        expect(lp1?.notation).toBe("40/4");
        expect(lp1?.isMaster).toBe(false);
        expect(lp1?.rootValue).toBe(4);
        expect(lp2?.notation).toBe("22/4");
        expect(lp2?.isMaster).toBe(true);
        expect(lp2?.heldMasterValue).toBe(22);
    });

    it("reports 44/8 as non-master", () => {
        const model = toProfilePresentationModel(v4Profile());
        const personality = model.atlasNumbers.find(
            (n) => n.label === "Persönlichkeit",
        );

        expect(personality?.notation).toBe("44/8");
        expect(personality?.isMaster).toBe(false);
        expect(personality?.rootValue).toBe(8);
    });

    it("maps cycles, pinnacles and challenges", () => {
        const model = toProfilePresentationModel(v4Profile());

        expect(model.personalYear?.notation).toBe("17/8");
        expect(model.personalYear?.rootValue).toBe(8);
        expect(model.personalMonth?.rootValue).toBe(1);
        expect(model.personalDay?.rootValue).toBe(9);
        expect(model.pinnacles.map((p) => p.notation)).toEqual([
            "16/7",
            "15/6",
            "13/4",
            "13/4",
        ]);
        expect(model.challenges.map((c) => c.value)).toEqual([2, 3, 1, 1]);
    });
});

describe("toProfilePresentationModel (V1/V3)", () => {
    it("maps legacy NumberResult fields via reduced_value", () => {
        const legacy = {
            schema_version: "profile-calculation-result-v3",
            deterministic_hash: "b".repeat(64),
            input_ref: { core_name: "Anna Beispiel", birth_date: "1990-05-12" },
            policy: { version: "v1" },
            life_path_primary: { reduced_value: 1, compound_notation: "1" },
            life_path_secondary: { reduced_value: 2, compound_notation: "2" },
            birthday: { reduced_value: 3, compound_notation: "3" },
            attitude: { reduced_value: 4, compound_notation: "4" },
            core_name: {
                expression: { reduced_value: 5, compound_notation: "5" },
                soul_urge: { reduced_value: 6, compound_notation: "6" },
                personality: { reduced_value: 7, compound_notation: "7" },
            },
            cycles: {
                personal_year: { reduced_value: 8 },
                personal_month: { reduced_value: 9 },
                personal_day: { reduced_value: 1 },
                pinnacles: [],
                challenges: [],
            },
        };

        const model = toProfilePresentationModel(legacy);

        expect(model.name).toBe("Anna Beispiel");
        expect(model.methodVersion).toBe("v1");
        expect(model.atlasNumbers[0].notation).toBe("1");
        expect(model.atlasNumbers[0].rootValue).toBe(1);
        expect(model.personalYear?.rootValue).toBe(8);
    });

    it("handles missing optional names without crashing", () => {
        const minimal = {
            schema_version: "profile-calculation-result-v3",
            deterministic_hash: "c".repeat(64),
            input_ref: { core_name: "Nur Name" },
            policy: { version: "v1" },
            life_path_primary: { reduced_value: 1 },
            life_path_secondary: { reduced_value: 2 },
            birthday: { reduced_value: 3 },
            attitude: { reduced_value: 4 },
            cycles: {},
        };

        const model = toProfilePresentationModel(minimal);

        expect(model.name).toBe("Nur Name");
        expect(model.atlasNumbers).toHaveLength(8);
        expect(model.personalYear).toBeNull();
        expect(model.personalMonth).toBeNull();
        expect(model.personalDay).toBeNull();
    });

    it("handles unknown schema versions and damaged data without silent wrong values", () => {
        const damaged = {
            schema_version: "profile-calculation-result-unknown",
            deterministic_hash: "d".repeat(64),
            input_ref: { core_name: "Kaputt" },
            policy: { version: "v9" },
            life_path_primary: { reduced_value: 7 },
            life_path_secondary: null,
            birthday: null,
            attitude: { reduced_value: 4 },
            cycles: { personal_year: { reduced_value: 0 } },
        };

        const model = toProfilePresentationModel(damaged);

        expect(model.schemaVersion).toBe("profile-calculation-result-unknown");
        expect(model.methodVersion).toBe("v9");
        // Missing models fall back to the em-dash placeholder, never to a wrong number.
        expect(model.atlasNumbers[1].notation).toBe("—");
        expect(model.atlasNumbers[1].rootValue).toBe(0);
        expect(model.atlasNumbers[2].notation).toBe("—");
        expect(model.personalYear).toBeNull();
    });

    it("supports numeric challenges and object challenges", () => {
        const profile = {
            schema_version: "profile-calculation-result-v3",
            deterministic_hash: "e".repeat(64),
            input_ref: { core_name: "Zyklen" },
            policy: { version: "v1" },
            life_path_primary: { reduced_value: 1 },
            life_path_secondary: { reduced_value: 2 },
            birthday: { reduced_value: 3 },
            attitude: { reduced_value: 4 },
            cycles: {},
            pinnacles: [{ reduced_value: 7 }],
            challenges: [2, { reduced_value: 3 }],
        };

        const model = toProfilePresentationModel(profile);

        expect(model.pinnacles[0].rootValue).toBe(7);
        expect(model.challenges.map((c) => c.value)).toEqual([2, 3]);
    });
});
