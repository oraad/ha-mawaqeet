import { css } from "lit";

export const cardStyles = css`
  :host {
    display: block;
    height: 100%;
  }

  ha-card {
    height: 100%;
    overflow: hidden;
    padding: 16px;
    display: flex;
    flex-direction: column;
  }

  .header {
    font-size: 0.85em;
    opacity: 0.7;
    margin-bottom: 8px;
  }

  .error {
    color: var(--error-color, #b71c1c);
    padding: 8px 0;
  }

  .icon-slot {
    width: 24px;
    flex-shrink: 0;
    display: grid;
    place-items: center;
  }

  .row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 4px;
    border-radius: 8px;
    cursor: pointer;
  }

  .row:hover {
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.05));
  }

  .row.next {
    font-weight: 600;
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
    box-shadow: inset 3px 0 0 var(--primary-color);
  }

  .row.passed,
  .chip.passed,
  .timeline-marker.passed {
    opacity: 0.6;
    color: var(--secondary-text-color);
  }

  .row.passed ha-icon,
  .chip.passed ha-icon,
  .timeline-marker.passed ha-icon {
    color: var(--secondary-text-color);
  }

  .row ha-icon,
  .chip ha-icon {
    --mdc-icon-size: 22px;
    color: var(--primary-color);
  }

  .row .name {
    flex: 1;
    min-width: 0;
  }

  .row .times {
    text-align: end;
    white-space: nowrap;
  }

  .row .relative {
    font-size: 0.75em;
    opacity: 0.7;
  }

  .next-hero {
    text-align: center;
    padding: 8px 0 16px;
    cursor: pointer;
  }

  .next-hero .icon-slot {
    width: auto;
    margin: 0 auto;
  }

  .next-hero ha-icon {
    --mdc-icon-size: 40px;
    color: var(--primary-color);
  }

  .next-hero .prayer-name {
    font-size: 1.5em;
    font-weight: 600;
    margin: 8px 0 4px;
  }

  .next-hero .countdown {
    font-size: 1.35em;
    color: var(--primary-color);
    font-weight: 600;
  }

  .next-hero .at-time {
    font-size: 0.95em;
    opacity: 0.75;
    margin-top: 2px;
  }

  .next-hero .tomorrow-badge {
    display: inline-block;
    margin-top: 8px;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75em;
    font-weight: 600;
    color: var(--primary-color);
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
  }

  .next-hero .following {
    font-size: 0.85em;
    opacity: 0.7;
    margin-top: 8px;
  }

  .horizontal {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    align-items: stretch;
  }

  .chip {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 8px;
    border-radius: 8px;
    min-width: 4.5em;
    border: 1px solid transparent;
    cursor: pointer;
    gap: 2px;
  }

  .chip.next {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
    font-weight: 600;
  }

  .chip .chip-time {
    font-size: 0.95em;
    margin-top: 2px;
  }

  .chip .chip-relative {
    font-size: 0.7em;
    opacity: 0.7;
  }

  .divider {
    border: none;
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
    margin: 12px 0;
  }

  .section-title {
    font-size: 0.75em;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    opacity: 0.6;
    margin: 12px 0 6px;
  }

  .agenda-empty {
    font-size: 0.9em;
    opacity: 0.65;
    padding: 4px 0 8px;
  }

  .agenda-status {
    width: 20px;
    flex-shrink: 0;
    display: grid;
    place-items: center;
    color: var(--secondary-text-color);
  }

  .agenda-status ha-icon {
    --mdc-icon-size: 18px;
    color: var(--secondary-text-color);
  }

  .timeline {
    position: relative;
    height: 80px;
    margin: 28px 12px 36px;
  }

  .timeline-track {
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    height: 4px;
    background: var(--divider-color, rgba(0, 0, 0, 0.15));
    border-radius: 2px;
    transform: translateY(-50%);
  }

  .timeline-marker {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    text-align: center;
    font-size: 0.72em;
    white-space: nowrap;
    cursor: pointer;
  }

  .timeline-marker .icon-slot {
    width: auto;
    margin: 0 auto;
  }

  .timeline-marker ha-icon {
    --mdc-icon-size: 18px;
    color: var(--primary-color);
  }

  .timeline-marker.next {
    font-weight: 600;
  }

  .timeline-marker.next ha-icon {
    --mdc-icon-size: 20px;
  }

  .timeline-now {
    position: absolute;
    top: -4px;
    width: 2px;
    height: 88px;
    background: var(--accent-color, var(--primary-color));
    transform: translateX(-50%);
    z-index: 1;
  }
`;
