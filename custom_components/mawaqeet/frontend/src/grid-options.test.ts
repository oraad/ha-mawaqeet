import { describe, expect, it } from "vitest";
import { gridOptionsForLayout } from "./grid-options";
import type { CardLayout } from "./types";

describe("gridOptionsForLayout", () => {
  it("returns compact defaults for next layout", () => {
    expect(gridOptionsForLayout("next")).toEqual({
      columns: 6,
      rows: 2,
      min_rows: 2,
      min_columns: 3,
    });
  });

  it("returns full-width auto height for horizontal and combined", () => {
    const expected = {
      columns: 12,
      rows: "auto",
      min_rows: 2,
      min_columns: 6,
    };
    expect(gridOptionsForLayout("horizontal")).toEqual(expected);
    expect(gridOptionsForLayout("combined")).toEqual(expected);
  });

  it("returns fixed rows for timeline", () => {
    expect(gridOptionsForLayout("timeline")).toEqual({
      columns: 12,
      rows: 3,
      min_rows: 3,
      max_rows: 4,
    });
  });

  it("returns tall auto rows for vertical and agenda", () => {
    const expected = {
      columns: 6,
      rows: "auto",
      min_rows: 4,
      min_columns: 3,
    };
    expect(gridOptionsForLayout("vertical")).toEqual(expected);
    expect(gridOptionsForLayout("agenda")).toEqual(expected);
  });

  it("falls back to next layout for unknown values", () => {
    expect(gridOptionsForLayout("unknown" as CardLayout)).toEqual(
      gridOptionsForLayout("next"),
    );
  });
});
