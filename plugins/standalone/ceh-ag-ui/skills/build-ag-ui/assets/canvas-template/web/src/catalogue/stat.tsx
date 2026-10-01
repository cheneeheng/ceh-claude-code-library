import { z } from "zod";
import { defineComponent } from "./define";

export const stat = defineComponent({
  name: "show_stat",
  description:
    "One headline number with its label and optional change versus a previous period. Use for a single KPI; use show_bar_chart to compare several.",
  schema: z.object({
    label: z.string(),
    value: z.number(),
    unit: z.string().optional(),
    change: z.number().optional().describe("Percent change; negative for a decrease"),
  }),
  example: { label: "Active users", value: 12840, change: 4.2 },
  Component: ({ label, value, unit, change }) => (
    <article className="card" aria-label={label}>
      <p className="eyebrow">{label}</p>
      <p className="stat-value numeric">
        {value.toLocaleString()}
        {unit && <span className="muted"> {unit}</span>}
      </p>
      {change !== undefined && (
        // The sign picks the colour, never the agent.
        <p className={`numeric ${change < 0 ? "text-danger" : "text-success"}`}>
          {change > 0 ? "+" : ""}
          {change}%
        </p>
      )}
    </article>
  ),
});
