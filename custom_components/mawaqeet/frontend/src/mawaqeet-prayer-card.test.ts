import { describe, expect, it } from "vitest";
import { gridOptionsForLayout } from "./grid-options";
import { MawaqeetPrayerCard } from "./mawaqeet-prayer-card";
import type { CardLayout, MawaqeetCardConfig } from "./types";

function cardWithLayout(layout: CardLayout): MawaqeetPrayerCard {
  const card = Object.create(
    MawaqeetPrayerCard.prototype,
  ) as MawaqeetPrayerCard;
  const config: MawaqeetCardConfig = {
    type: "custom:mawaqeet-prayer-card",
    device: "device-1",
    layout,
  };
  Object.defineProperty(card, "_config", { value: config, writable: true });
  return card;
}

describe("MawaqeetPrayerCard sizing", () => {
  it("getGridOptions matches gridOptionsForLayout per layout", () => {
    const layouts: CardLayout[] = [
      "next",
      "horizontal",
      "vertical",
      "combined",
      "timeline",
      "agenda",
    ];
    for (const layout of layouts) {
      const card = cardWithLayout(layout);
      expect(card.getGridOptions()).toEqual(gridOptionsForLayout(layout));
    }
  });

  it("getCardSize returns legacy masonry heights", () => {
    expect(cardWithLayout("next").getCardSize()).toBe(2);
    expect(cardWithLayout("horizontal").getCardSize()).toBe(2);
    expect(cardWithLayout("combined").getCardSize()).toBe(2);
    expect(cardWithLayout("vertical").getCardSize()).toBe(4);
    expect(cardWithLayout("agenda").getCardSize()).toBe(4);
    expect(cardWithLayout("timeline").getCardSize()).toBe(3);
  });
});
