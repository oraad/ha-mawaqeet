import type { CardLayout, LovelaceGridOptions } from "./types";

/** Default grid sizing per layout for Sections dashboards. */
export function gridOptionsForLayout(layout: CardLayout): LovelaceGridOptions {
  switch (layout) {
    case "horizontal":
    case "combined":
      return {
        columns: 12,
        rows: "auto",
        min_rows: 2,
        min_columns: 6,
      };
    case "timeline":
      return {
        columns: 12,
        rows: 3,
        min_rows: 2,
        max_rows: 4,
      };
    case "vertical":
    case "agenda":
      return {
        columns: 6,
        rows: "auto",
        min_rows: 4,
        min_columns: 3,
      };
    case "next":
    default:
      return {
        columns: 6,
        rows: 2,
        min_rows: 2,
        min_columns: 3,
      };
  }
}
