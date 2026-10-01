import { HttpAgent, randomUUID, type Message, type RunAgentParameters } from "@ag-ui/client";
import { useEffect, useMemo, useState } from "react";
import { z } from "zod";
import type { CanvasComponent } from "./catalogue";

export type Block = { id: string; name: string; props: Record<string, unknown> };

// Stops an agent that keeps calling tools from looping forever.
const MAX_TOOL_ROUNDS = 5;

export function useAgent(catalogue: CanvasComponent[]) {
  const agent = useMemo(
    () => new HttpAgent({ url: import.meta.env.VITE_AGENT_URL ?? "/agent" }),
    [],
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const sub = agent.subscribe({ onMessagesChanged: ({ messages }) => setMessages([...messages]) });
    return () => sub.unsubscribe();
  }, [agent]);

  // Only the parsed result reaches a component: unknown keys are stripped, so the agent can
  // neither style a component nor pass it anything its schema does not declare.
  function render(name: string, rawArgs: string, id: string): string {
    const entry = catalogue.find((c) => c.name === name)!;
    let args: unknown;
    try {
      args = JSON.parse(rawArgs || "{}");
    } catch {
      return "error: arguments were not valid JSON";
    }
    const parsed = entry.schema.safeParse(args);
    if (!parsed.success) return `error: ${z.prettifyError(parsed.error)}`;
    setBlocks((b) => [...b, { id, name, props: parsed.data }]);
    return "rendered";
  }

  const tools = catalogue.map(({ name, description, parameters, example }) => ({
    name,
    description,
    parameters,
    metadata: { example },
  }));

  // One user action = runs until the agent stops calling catalogue tools.
  async function drive(params: RunAgentParameters = {}) {
    setRunning(true);
    setError(null);
    try {
      for (let round = 0; round < MAX_TOOL_ROUNDS; round++) {
        const { newMessages } = await agent.runAgent({ ...params, tools });
        params = {};
        const calls = newMessages
          .flatMap((m) => (m.role === "assistant" ? (m.toolCalls ?? []) : []))
          .filter((c) => catalogue.some((entry) => entry.name === c.function.name));
        if (calls.length === 0) break;
        for (const call of calls) {
          const content = render(call.function.name, call.function.arguments, call.id);
          agent.addMessage({ id: randomUUID(), role: "tool", toolCallId: call.id, content });
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  async function send(text: string) {
    agent.addMessage({ id: randomUUID(), role: "user", content: text });
    await drive();
  }

  return { messages, blocks, running, error, send, abort: () => agent.abortRun() };
}
