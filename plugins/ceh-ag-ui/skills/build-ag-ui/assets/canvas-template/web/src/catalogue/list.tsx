import { z } from "zod";
import { defineComponent } from "./define";

export const list = defineComponent({
  name: "show_list",
  description: "A titled list of short items. Set ordered when the order matters, such as steps.",
  schema: z.object({ title: z.string(), items: z.array(z.string()).min(1), ordered: z.boolean().default(false) }),
  example: { title: "Next steps", items: ["Confirm the budget", "Book the venue"], ordered: true },
  Component: ({ title, items, ordered }) => {
    const Tag = ordered ? "ol" : "ul";
    return (
      <article className="card">
        <h2>{title}</h2>
        <Tag>{items.map((item, i) => <li key={i}>{item}</li>)}</Tag>
      </article>
    );
  },
});
