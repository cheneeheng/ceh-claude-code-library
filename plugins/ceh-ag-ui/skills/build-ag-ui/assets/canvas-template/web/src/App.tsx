import { useState, type FormEvent } from "react";
import { catalogue } from "./catalogue";
import { useAgent } from "./useAgent";

// "show_bar_chart" -> "bar chart": the phrase the mock agent listens for.
const phrase = (name: string) => name.replace(/^show_/, "").replaceAll("_", " ");

export function App() {
  const { messages, blocks, running, error, send, abort } = useAgent(catalogue);
  const [draft, setDraft] = useState("");

  function submit(text: string) {
    if (!text.trim() || running) return;
    setDraft("");
    void send(text.trim());
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    submit(draft);
  }

  return (
    <div className="shell">
      <main className="canvas" aria-label="Canvas">
        {blocks.length === 0 ? (
          <section className="canvas-empty">
            <p className="eyebrow">Canvas</p>
            <h1>Ask for something to see it here</h1>
            <p className="muted">The agent answers with components from this app's catalogue.</p>
            <div className="starters">
              {catalogue.slice(0, 4).map((c) => (
                <button key={c.name} type="button" className="btn btn-outline btn-sm" onClick={() => submit(`Show a ${phrase(c.name)}`)}>
                  Show a {phrase(c.name)}
                </button>
              ))}
            </div>
          </section>
        ) : (
          blocks.map((block) => {
            const Component = catalogue.find((c) => c.name === block.name)!.Component;
            return <Component key={block.id} {...block.props} />;
          })
        )}
      </main>

      <aside className="chat" aria-label="Conversation">
        <ol className="messages" aria-live="polite">
          {messages
            .filter((m) => (m.role === "user" || m.role === "assistant") && typeof m.content === "string" && m.content)
            .map((m) => (
              <li key={m.id} className={m.role}>
                {m.content as string}
              </li>
            ))}
        </ol>
        {error && <p role="alert" className="text-danger chat-error">{error}</p>}
        <form onSubmit={onSubmit}>
          <label htmlFor="prompt" className="visually-hidden">Message the agent</label>
          <input id="prompt" className="input" value={draft} onChange={(e) => setDraft(e.target.value)} autoComplete="off" placeholder="Message the agent" />
          {running ? (
            <button type="button" className="btn btn-outline" onClick={abort}>Stop</button>
          ) : (
            <button type="submit" className="btn btn-primary">Send</button>
          )}
        </form>
      </aside>
    </div>
  );
}
