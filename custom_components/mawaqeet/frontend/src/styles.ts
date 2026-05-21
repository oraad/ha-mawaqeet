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
    margin-bottom: 12px;
  }

  .error {
    color: var(--error-color, #b71c1c);
    padding: 8px 0;
  }

  .row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 4px;
    border-radius: 8px;
    cursor: pointer;
  }

  .row:hover {
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.05));
  }

  .row.next {
    font-weight: 600;
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
  }

  .row.passed {
    opacity: 0.45;
  }

  .row.passed.strike {
    text-decoration: line-through;
  }

  .row ha-icon {
    --mdc-icon-size: 22px;
    color: var(--primary-color);
    flex-shrink: 0;
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
  }

  .next-hero ha-icon {
    --mdc-icon-size: 48px;
    color: var(--primary-color);
  }

  .next-hero .prayer-name {
    font-size: 1.5em;
    font-weight: 600;
    margin: 8px 0 4px;
  }

  .next-hero .countdown {
    font-size: 1.25em;
    color: var(--primary-color);
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
    padding: 8px 10px;
    border-radius: 8px;
    min-width: 4.5em;
    border: 1px solid transparent;
    cursor: pointer;
  }

  .chip.next {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
    font-weight: 600;
  }

  .chip.passed {
    opacity: 0.45;
  }

  .chip ha-icon {
    --mdc-icon-size: 20px;
    color: var(--primary-color);
  }

  .chip .chip-time {
    font-size: 0.95em;
    margin-top: 4px;
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
    opacity: 0.6;
    margin: 8px 0 4px;
  }

  .timeline {
    position: relative;
    height: 48px;
    margin: 24px 8px 32px;
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
    font-size: 0.65em;
    white-space: nowrap;
  }

  .timeline-marker ha-icon {
    --mdc-icon-size: 16px;
    color: var(--primary-color);
  }

  .timeline-now {
    position: absolute;
    top: -4px;
    width: 2px;
    height: 56px;
    background: var(--accent-color, var(--primary-color));
    transform: translateX(-50%);
    z-index: 1;
  }

  .agenda-check {
    opacity: 0.5;
    margin-inline-end: 4px;
  }
`;
