import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { NumberAtlas } from "./NumberAtlas";

describe("NumberAtlas", () => {
  it("shows calculation claims and reveals expert provenance on request", async () => {
    const user = userEvent.setup();

    render(
      <NumberAtlas
        hash={"c".repeat(64)}
        numbers={[
          { label: "Lebensweg", value: 1, notation: "37/10/1" },
          { label: "Ausdruck", value: 5, notation: "50/5" },
        ]}
      />,
    );

    expect(screen.getAllByLabelText("Aussageklasse Berechnung")).toHaveLength(2);
    expect(screen.getByRole("table", { name: "Tabellarischer Zahlenatlas" })).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Expertenansicht öffnen" }));
    expect(screen.getByText(/Berechnungshash/)).toBeVisible();
    expect(screen.getAllByText("37/10/1")).toHaveLength(2);
  });
});
