# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Stick to the Brief

**`consigne.md` is the contract. Nothing else gets built.**

- Every file in this repo must map to a line in the checklist of `consigne.md` (section 7), or to an
  addition listed in section 8 (« Au-delà du POC »).
- The V2 adds exactly two things beyond the brief: `api/` (FastAPI, exposes `src/rag.py` to the
  browser) and `web/` (Next.js interface). Nothing else: no Docker, no database, no conversation
  history sent to the model, no cloud deployment.
- The deposited version is frozen under the tag `depot-openclassrooms-2026-09-25`.
- Answer the question that was asked. Not the adjacent one, not the one you would have preferred.
- The technologies are imposed (Python 3, venv, pandas, OpenAgenda API, Mistral API, Faiss, LangChain).
  Do not substitute a "better" library.

## 6. Code That Does Not Read Like AI

**This is a student project defended orally. Every line must be explainable in one sentence.**

- 30 lines beat 300. If a script does not fit on one screen, it is doing too much.
- No banner comments, no `# ===== STEP 1 =====` dividers, no emoji in code.
- Comments explain *why*, never *what*. If the line is self-evident, say nothing.
- Docstrings where the brief requires them (pre-processing and vectorisation scripts): one short
  paragraph. Not an Args/Returns/Raises/Examples template on a three-line function.
- No try/except around things that cannot fail. In a POC, let it crash with a real traceback.
- No config classes, no factories, no `utils.py` grab-bag, no abstract base class for one implementation.
- Plain names: `events`, `index`, `query` — not `EventCollectionManager`.
- Standard library and pandas before adding a dependency.

## 7. Tooling

- `graphify` (`~/.claude/skills/graphify/SKILL.md`) is available for exploring the project as a
  knowledge graph. Trigger: `/graphify`.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
