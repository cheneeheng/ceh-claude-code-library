import { z } from "zod";
import { defineComponent } from "./define";

export const note = defineComponent({
  name: "show_note",
  description: "A titled block of prose. Use for an explanation or summary; not for data.",
  schema: z.object({ title: z.string(), body: z.string() }),
  example: { title: "Summary", body: "Revenue grew in every region this quarter." },
  Component: ({ title, body }) => (
    <article className="card">
      <h2>{title}</h2>
      <p>{body}</p>
    </article>
  ),
});
