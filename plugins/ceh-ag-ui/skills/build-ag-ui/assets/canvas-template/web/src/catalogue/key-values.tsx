import { z } from "zod";
import { defineComponent } from "./define";

export const keyValues = defineComponent({
  name: "show_key_values",
  description: "Labelled facts about one thing, such as a record's details. Use for one item; use show_table for many.",
  schema: z.object({
    title: z.string(),
    items: z.array(z.object({ key: z.string(), value: z.union([z.string(), z.number()]) })).min(1),
  }),
  example: { title: "Order #1042", items: [{ key: "Status", value: "Shipped" }, { key: "Total", value: "$129.00" }] },
  Component: ({ title, items }) => (
    <article className="card">
      <h2>{title}</h2>
      <dl className="key-values">
        {items.map(({ key, value }) => (
          <div key={key}>
            <dt className="muted">{key}</dt>
            <dd className={typeof value === "number" ? "numeric" : undefined}>{value}</dd>
          </div>
        ))}
      </dl>
    </article>
  ),
});
