import { describe, expect, it } from "vitest";

import { applyTheme, readTheme } from "./theme";

describe("theme preference", () => {
  it("persists and applies an explicit light theme", () => {
    applyTheme("light");

    expect(document.documentElement.dataset.theme).toBe("light");
    expect(localStorage.getItem("numra:theme")).toBe("light");
    expect(readTheme()).toBe("light");
  });
});
