import type { ComponentType } from "react";
import { z } from "zod";

// Props that would hand styling to the agent. Look is fixed at build time by the theme, so no
// schema may expose them; a visual choice the agent does need is a semantic enum (`tone`).
const STYLE_KEY = /^(style|class(name)?|css|theme|colou?r|background|font.*|size|width|height|variant)$/i;

export type CanvasComponent = {
  name: string;
  description: string;
  schema: z.ZodObject;
  parameters: Record<string, unknown>;
  example: Record<string, unknown>;
  Component: ComponentType<any>;
};

function assertNoStyleKeys(name: string, node: unknown): void {
  if (!node || typeof node !== "object") return;
  const props = (node as { properties?: Record<string, unknown> }).properties ?? {};
  for (const [key, child] of Object.entries(props)) {
    if (STYLE_KEY.test(key)) throw new Error(`${name}: "${key}" lets the agent style the component`);
    assertNoStyleKeys(name, child);
  }
  assertNoStyleKeys(name, (node as { items?: unknown }).items);
}

// One catalogue entry = one frontend tool. Fails at startup, not in front of a user, when the
// name is not snake_case, the schema exposes styling, or the example no longer fits the schema.
export function defineComponent<S extends z.ZodObject>(entry: {
  name: string;
  description: string;
  schema: S;
  example: z.input<S>;
  Component: ComponentType<z.output<S>>;
}): CanvasComponent {
  if (!/^[a-z][a-z0-9_]*$/.test(entry.name)) throw new Error(`${entry.name}: use snake_case`);
  const parameters = z.toJSONSchema(entry.schema) as Record<string, unknown>;
  assertNoStyleKeys(entry.name, parameters);
  entry.schema.parse(entry.example);
  return { ...entry, parameters, example: entry.example as Record<string, unknown> };
}
