import { z } from "zod";
import { defineComponent } from "./define";

const cell = z.union([z.string(), z.number()]);

export const table = defineComponent({
  name: "show_table",
  description: "Rows of records with named columns. Use when the user needs to scan or compare records.",
  schema: z.object({
    title: z.string(),
    columns: z.array(z.string()).min(1),
    rows: z.array(z.array(cell)).describe("Each row has one cell per column, in column order"),
  }),
  example: {
    title: "Top regions",
    columns: ["Region", "Orders", "Revenue"],
    rows: [["North", 412, "$38,200"], ["South", 367, "$31,900"]],
  },
  Component: ({ title, columns, rows }) => (
    <article className="card">
      <table className="table">
        <caption>{title}</caption>
        <thead>
          <tr>{columns.map((c) => <th key={c} scope="col">{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map((c, j) => (
                <td key={c} className={typeof row[j] === "number" ? "numeric" : undefined}>{row[j] ?? ""}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  ),
});
