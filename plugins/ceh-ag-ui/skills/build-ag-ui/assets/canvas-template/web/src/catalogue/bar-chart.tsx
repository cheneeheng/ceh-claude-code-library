import { z } from "zod";
import { defineComponent } from "./define";

export const barChart = defineComponent({
  name: "show_bar_chart",
  description: "Compare a handful of values by length, such as totals per category. Up to about 12 bars.",
  schema: z.object({
    title: z.string(),
    unit: z.string().optional(),
    bars: z.array(z.object({ label: z.string(), value: z.number().nonnegative() })).min(1).max(12),
  }),
  example: { title: "Signups by channel", bars: [{ label: "Search", value: 540 }, { label: "Social", value: 310 }, { label: "Email", value: 190 }] },
  Component: ({ title, unit, bars }) => {
    const max = Math.max(...bars.map((b) => b.value)) || 1;
    return (
      <article className="card">
        <h2>{title}</h2>
        <ul className="bar-chart">
          {bars.map((bar, i) => (
            <li key={bar.label}>
              <span>{bar.label}</span>
              <span className="numeric">
                {bar.value.toLocaleString()}
                {unit && ` ${unit}`}
              </span>
              {/* Width comes from the data; the series colour from the theme's data ramp. */}
              <div className="bar-track" aria-hidden="true">
                <div className={`bar-fill is-${(i % 4) + 1}`} style={{ width: `${(bar.value / max) * 100}%` }} />
              </div>
            </li>
          ))}
        </ul>
      </article>
    );
  },
});
