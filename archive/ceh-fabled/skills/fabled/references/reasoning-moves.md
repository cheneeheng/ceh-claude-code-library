# Reasoning Moves — The Deep Thinking Toolkit

Load this file for any hard task, and whenever the first decomposition fails, the problem is novel, or reasoning has stalled. These are the moves that convert thinking _time_ into thinking _quality_. High thinking effort without these degenerates into rumination.

## Scratchpad structure

Every extended reasoning pass follows this skeleton, explicitly:

1. **Goal** — one sentence: what does a complete, correct answer contain?
2. **Knowns / unknowns** — what is given, what must be derived, what cannot be known from here.
3. **Plan** — the decomposition chosen and why (see below).
4. **Execution** — work each part; mark each sub-conclusion as verified, derived, or assumed.
5. **Check** — attack the result (adversarial review from the Core Loop), then confirm it answers the goal in step 1, not a drifted version of it.

If at step 5 the answer fails, return to step 3 with a _different_ plan, not the same plan run harder.

## Decomposition patterns

The choice of decomposition is often the whole ballgame. Candidate cuts:

- **By case** — partition the input space exhaustively, solve each region. Verify the cases are exhaustive and disjoint; most case-analysis errors are missing cases, not wrong cases.
- **By component** — split along structural seams (modules, stages, actors). Then check the _interfaces_: component decompositions fail at the joints, where responsibility is ambiguous.
- **By timeline** — order events; many "logic" problems are secretly sequencing problems. Ask what must be true before each step can occur.
- **By stakeholder / perspective** — for judgment questions, run the analysis once per affected party; conflicts between the runs locate the real tension.
- **By constraint** — list every constraint, find the binding one, and design around it first. Optimizing a non-binding constraint is wasted work.

If the problem resists one cut, try another before concluding it's hard. Problems that look intractable under one decomposition are frequently trivial under a different one.

## Directional moves

- **Backward chaining** — start from the desired end state and ask what must be true immediately before it, recursively, until reaching the givens. Especially strong for planning, proofs, and "how do I get to X" questions; forward search from the givens wanders.
- **Inversion** — instead of "how do I make this succeed," ask "what would guarantee failure?" and design to avoid each guarantee. Inversion surfaces risks that forward optimism filters out.
- **Solve a relaxed version first** — drop the hardest constraint, solve, then reintroduce it. The relaxed solution reveals the structure; the reintroduction reveals exactly what the hard constraint costs.
- **Solve a smaller instance** — n=2 or n=3 by hand, exhaustively. Generalize only after the small case is fully understood; a pattern extrapolated from an unverified small case compounds the error.

## Stress-testing moves

Apply these to any conclusion before accepting it:

- **Extreme-case testing** — does the claim hold at zero, at one, at infinity, when the quantities are equal, when they're maximally unequal? A rule that breaks at the boundary is not a rule; it's an approximation with an undisclosed domain.
- **Invariant checking** — identify a quantity that must be conserved (totals, counts, energy, money, monotonicity) and confirm the answer conserves it. Violated invariants catch errors that step-by-step re-reading misses, because they check the _result_ rather than the _derivation_.
- **Independent-path verification** — recompute or re-derive by a genuinely different route. Re-reading your own derivation mostly re-confirms your own blind spot; a different path shares no steps with it.
- **Order-of-magnitude anchor** — before or after any quantitative work, produce a crude Fermi estimate from different inputs. If the careful answer and the crude anchor disagree by 10x, one of them is wrong, and it is not always the careful one.
- **Steelman the opposite conclusion** — write the best three-sentence case that the answer is wrong. If that case is stronger than expected, the review found something real. If it's genuinely weak, confidence is now earned rather than assumed.

## Representation changes

When reasoning stalls, the representation is often the obstacle. Re-encode:

- Prose → table (when comparing entities across attributes)
- Prose → timeline (when order matters)
- Prose → algebra (when quantities interact; name the variables and the relations become checkable)
- Instance → general (when drowning in specifics, abstract the pattern)
- General → instance (when lost in abstraction, pick concrete numbers and run them)
- Verbal diagram — for structural problems, describe the graph explicitly: nodes, edges, direction. Cycles and orphans become visible.

The test of a good representation: steps that were arguments become mechanical, and errors that were invisible become visible.

## Analogy — with the disanalogy check

Analogies are powerful hypothesis generators and terrible verifiers. When importing a solution from an analogous domain, immediately list the ways the domains differ, and confirm none of the differences touches the load-bearing part of the imported solution. An analogy whose disanalogies were never checked is a guess wearing a suit.

## Managing the search

- **Breadth before depth at the start**: enumerate candidate approaches quickly and shallowly before investing deeply in one. Depth-first from the first idea is how hours get spent proving the wrong lemma.
- **Track dead ends explicitly**: when abandoning an approach, record _why_ in the scratchpad. Untracked dead ends get re-entered.
- **Notice the loop**: if the same intermediate conclusion has appeared twice with no new supporting work, the current strategy is exhausted. Change decomposition or representation — do not simply "think harder" in place.
- **Know when to stop**: stop when (a) the answer is verified by an independent path, (b) further passes produce refinements too small to change the verdict, or (c) the remaining uncertainty is irreducible from the available information — in which case, say exactly that and name what would resolve it.
