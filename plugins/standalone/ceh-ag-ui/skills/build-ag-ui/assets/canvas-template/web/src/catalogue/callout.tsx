import { z } from "zod";
import { defineComponent } from "./define";

// A semantic tone, not a colour: the theme decides what each one looks like.
const TONE_DOT = { info: "dot", success: "dot dot-success", warning: "dot dot-warning", danger: "dot dot-danger" };

export const callout = defineComponent({
  name: "show_callout",
  description: "A short message that needs attention: a result, a warning, or an error. Pick the tone by meaning.",
  schema: z.object({
    tone: z.enum(["info", "success", "warning", "danger"]),
    title: z.string(),
    body: z.string().optional(),
  }),
  example: { tone: "warning", title: "Budget at 90%", body: "Two campaigns will pause when it is reached." },
  Component: ({ tone, title, body }) => (
    <aside className="card has-edge" role={tone === "danger" ? "alert" : "note"}>
      <h2>
        <span className={TONE_DOT[tone]} aria-hidden="true" /> {title}
      </h2>
      {body && <p>{body}</p>}
    </aside>
  ),
});
