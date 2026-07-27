import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { PwaUpdateNotice } from "./PwaUpdateNotice";

describe("PwaUpdateNotice", () => {
  it("lets the user explicitly activate a waiting version", async () => {
    const update = vi.fn().mockResolvedValue(undefined);
    render(<PwaUpdateNotice updateAvailable onUpdate={update} onDismiss={vi.fn()} />);

    await userEvent.click(screen.getByRole("button", { name: /Jetzt aktualisieren/i }));

    expect(update).toHaveBeenCalledWith(true);
  });
});
