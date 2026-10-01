import { barChart } from "./bar-chart";
import { callout } from "./callout";
import type { CanvasComponent } from "./define";
import { keyValues } from "./key-values";
import { list } from "./list";
import { note } from "./note";
import { stat } from "./stat";
import { table } from "./table";

// Everything the agent can place on the canvas. Add a component: new file here, one line below.
export const catalogue: CanvasComponent[] = [note, stat, table, list, keyValues, callout, barChart];

export type { CanvasComponent };
