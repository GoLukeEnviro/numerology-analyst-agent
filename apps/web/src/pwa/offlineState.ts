/**
 * Offline state — reactive online/offline listener.
 *
 * Four discrete states replace a single boolean flag:
 * - PROFILE_CALCULATION_REQUIRES_NETWORK
 * - REPORT_GENERATION_REQUIRES_NETWORK
 * - SAVED_PROFILE_AVAILABLE_OFFLINE
 * - SAVED_REPORT_AVAILABLE_OFFLINE
 */
import { useEffect, useState } from "react";

export type OfflineCapability =
    | "PROFILE_CALCULATION_REQUIRES_NETWORK"
    | "REPORT_GENERATION_REQUIRES_NETWORK"
    | "SAVED_PROFILE_AVAILABLE_OFFLINE"
    | "SAVED_REPORT_AVAILABLE_OFFLINE";

export interface OfflineState {
    online: boolean;
    capabilities: Set<OfflineCapability>;
}

const initialState = (): OfflineState => ({
    online: typeof navigator !== "undefined" ? navigator.onLine : true,
    capabilities: new Set(),
});

export function useOfflineState(
    hasSavedProfile: boolean,
    hasSavedReport: boolean,
): OfflineState {
    const [state, setState] = useState<OfflineState>(initialState);

    useEffect(() => {
        const update = () => {
            setState(() => {
                const online = navigator.onLine;
                const capabilities = new Set<OfflineCapability>();

                if (!online) {
                    capabilities.add("PROFILE_CALCULATION_REQUIRES_NETWORK");
                    capabilities.add("REPORT_GENERATION_REQUIRES_NETWORK");
                }
                if (hasSavedProfile) {
                    capabilities.add("SAVED_PROFILE_AVAILABLE_OFFLINE");
                }
                if (hasSavedReport) {
                    capabilities.add("SAVED_REPORT_AVAILABLE_OFFLINE");
                }

                return { online, capabilities };
            });
        };

        window.addEventListener("online", update);
        window.addEventListener("offline", update);
        update();
        return () => {
            window.removeEventListener("online", update);
            window.removeEventListener("offline", update);
        };
    }, [hasSavedProfile, hasSavedReport]);

    return state;
}
