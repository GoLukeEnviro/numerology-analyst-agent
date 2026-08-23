import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useOfflineState } from "./offlineState";

afterEach(() => {
    vi.restoreAllMocks();
});

function setOnline(online: boolean) {
    vi.spyOn(window.navigator, "onLine", "get").mockReturnValue(online);
}

describe("useOfflineState", () => {
    it("reports online with no capabilities when nothing is saved", () => {
        setOnline(true);
        const { result } = renderHook(() =>
            useOfflineState(false, false),
        );

        expect(result.current.online).toBe(true);
        expect(result.current.capabilities.size).toBe(0);
    });

    it("adds network-required capabilities while offline", () => {
        setOnline(false);
        const { result } = renderHook(() =>
            useOfflineState(false, false),
        );

        expect(result.current.online).toBe(false);
        expect(result.current.capabilities.has("PROFILE_CALCULATION_REQUIRES_NETWORK")).toBe(true);
        expect(result.current.capabilities.has("REPORT_GENERATION_REQUIRES_NETWORK")).toBe(true);
    });

    it("adds saved-profile and saved-report capabilities", () => {
        setOnline(false);
        const { result } = renderHook(() =>
            useOfflineState(true, true),
        );

        expect(result.current.capabilities.has("SAVED_PROFILE_AVAILABLE_OFFLINE")).toBe(true);
        expect(result.current.capabilities.has("SAVED_REPORT_AVAILABLE_OFFLINE")).toBe(true);
    });

    it("reacts to online/offline window events", () => {
        setOnline(true);
        const { result } = renderHook(() =>
            useOfflineState(true, false),
        );

        expect(result.current.online).toBe(true);

        act(() => {
            setOnline(false);
            window.dispatchEvent(new Event("offline"));
        });

        expect(result.current.online).toBe(false);
        expect(result.current.capabilities.has("PROFILE_CALCULATION_REQUIRES_NETWORK")).toBe(true);
        expect(result.current.capabilities.has("SAVED_PROFILE_AVAILABLE_OFFLINE")).toBe(true);

        act(() => {
            setOnline(true);
            window.dispatchEvent(new Event("online"));
        });

        expect(result.current.online).toBe(true);
        expect(result.current.capabilities.has("PROFILE_CALCULATION_REQUIRES_NETWORK")).toBe(false);
    });

    it("removes event listeners on unmount", () => {
        setOnline(true);
        const removeSpy = vi.spyOn(window, "removeEventListener");
        const { unmount } = renderHook(() => useOfflineState(false, false));

        unmount();

        expect(removeSpy).toHaveBeenCalledWith("online", expect.any(Function));
        expect(removeSpy).toHaveBeenCalledWith("offline", expect.any(Function));
    });
});
