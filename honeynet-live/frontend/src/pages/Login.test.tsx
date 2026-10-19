import { describe, expect, it } from "vitest";

describe("banner logic", () => {
  it("labels demo vs live", () => {
    const banner = (liveEvents: number, mode: string) =>
      liveEvents > 0 && mode !== "demo" ? "LIVE DATA" : "DEMO DATA";
    expect(banner(0, "demo")).toBe("DEMO DATA");
    expect(banner(3, "live")).toBe("LIVE DATA");
  });
});
