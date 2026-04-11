# OEISGame Roadmap

This roadmap turns the current CLI prototype into a replayable deckbuilder with clear delivery milestones.

## Current baseline (April 2026)

- Deterministic card cycling combat loop.
- Three starter enemies with constraints and scoring.
- Sequence transforms as the core mechanic.
- Lightweight tests around scoring, constraints, and simulation sanity.

---

## North-star goals

1. **Strategic runs over deterministic demos**: player decisions should matter every turn.
2. **Readable sequence-first UX**: sequence state and transformations must stay legible.
3. **Fast iteration loop**: maintain simple architecture + strong tests so new cards/enemies are easy to add.

---

## Milestone plan

## M1 — Core deckbuilder loop (1–2 weeks)

**Objective:** replace deterministic cycling with real card-play choices.

### Scope
- Hand/draw/discard system.
- Turn energy + card costs.
- Explicit turn phases (`draw -> play -> end`).
- Basic status text in CLI showing hand, energy, and chosen card.

### Definition of done
- Player can choose from a hand each turn.
- Deck exhaustion reshuffles discard into draw pile.
- Tests cover draw/discard reshuffle, energy spend validation, and invalid-play guards.

### Suggested implementation order
1. Add `CombatDeckState` model (`draw_pile`, `hand`, `discard_pile`, `exhaust_pile`).
2. Refactor `play_battle` into phase helpers (`start_turn`, `play_card`, `resolve_end_turn`).
3. Add CLI input adapter (with deterministic fallback for tests).
4. Add tests for new state transitions.

---

## M2 — Enemy interaction depth (1 week)

**Objective:** make enemies feel distinct and reactive.

### Scope
- Enemy intents (`buff`, `debuff`, `disrupt`, `scale`).
- Anti-cards or sequence effects (e.g., truncate sequence, negate growth, inject noise).
- Telegraph intents one turn ahead.

### Definition of done
- Each starter enemy has at least 2 intent types.
- Enemy turn effects alter player decision-making.
- Battle log clearly records enemy intent and its impact.

### Suggested implementation order
1. Add `EnemyIntent` model + per-turn intent selection.
2. Implement effect pipeline after player action.
3. Add enemy-specific AI tables.
4. Extend tests for intent determinism and effect correctness.

---

## M3 — Run structure and progression (1–2 weeks)

**Objective:** support full runs instead of isolated battles.

### Scope
- Node-based map (combat, event, rest, elite).
- Rewards after combat (new card, upgrade, heal, relic-lite passive).
- Run state persistence for a single session.

### Definition of done
- A complete run contains 5–8 nodes and a final encounter.
- At least one meaningful reward choice after each combat.
- Run summary printed at the end.

### Suggested implementation order
1. Add `RunState` and map generator.
2. Implement post-combat reward screens in CLI.
3. Add card-upgrade data model.
4. Add deterministic seeds for reproducible tests.

---

## M4 — Content expansion and balancing (ongoing)

**Objective:** increase replayability.

### Scope
- Expand card set (arithmetic, recurrence, filtering, permutation families).
- Add 3–5 new enemies and one boss with multi-phase constraints.
- Introduce rarity and encounter pools.

### Definition of done
- 30+ cards, 8+ enemies, 1 boss.
- No single strategy dominates benchmark seeds.
- Constraint and scoring semantics are documented.

---

## M5 — Basic web UI (parallel/after M2)

**Objective:** make sequence evolution more readable and demo-friendly.

### Scope
- Minimal web interface for turn-by-turn sequence visualization.
- Log panel, hand panel, and enemy intent panel.
- Keep game logic in shared engine module; UI as thin layer.

### Definition of done
- Same combat engine can run in CLI and web front-end.
- Visual timeline of sequence mutations per turn.

---

## Engineering track (cross-cutting)

### Architecture
- Keep pure game logic framework-agnostic in `src/oeisgame.py` (or split into `engine/`).
- Isolate I/O adapters (CLI now, web later).
- Use explicit state objects rather than ad-hoc dicts.

### Quality
- Grow tests along seams: scoring, constraints, turn phases, enemy intents, reward generation.
- Add snapshot-style tests for battle logs on fixed seeds.
- Add lint + format checks in CI.

### Observability
- Add optional structured turn events for debugging and replay.
- Include random seed in every run log.

---

## Immediate next sprint backlog (recommended)

1. **Refactor:** extract combat state machine from `play_battle`.
2. **Feature:** implement draw/hand/discard and deterministic draw order for tests.
3. **Feature:** add energy + card costs with clear invalid-play feedback.
4. **CLI:** prompt player to choose cards from hand.
5. **Tests:** add unit tests for reshuffle + energy rules + turn flow.
6. **Docs:** update README examples to reflect interactive turns.

---

## New Game+ sketch (post-M5 / replayability track)

**Goal:** keep runs fresh after first win by adding opt-in escalating modifiers that stress different sequence skills.

### Core model

- Add `ascension_level: int = 0` to `RunState` (0 = base game).
- Add an `AscensionRule` concept with:
  - `name`
  - `level_unlock`
  - `description`
  - `apply_to_run(run_state)` and/or `apply_to_battle(state)` hooks.
- At run start, enable all rules with `level_unlock <= ascension_level`.

### Suggested level ladder (A1–A10)

1. **A1: Frail Start** — start each run at `max_hp - 5`.
2. **A2: Tighter Clock** — normal combats reduced by 1 turn.
3. **A3: Lean Rewards** — reward screen offers 2 options instead of 3.
4. **A4: Elite Pressure** — map generator increases elite node frequency.
5. **A5: Intent Foresight Tax** — enemy intent telegraph hidden every other turn.
6. **A6: Cost Inflation** — random card in opening hand costs +1 energy this turn.
7. **A7: Relic Scarcity** — relic reward chance reduced.
8. **A8: Corruption Pulse** — every 3 turns, append low-amplitude noise term.
9. **A9: Boss Endurance** — boss HP +20% and phase fail penalty +1.
10. **A10: Entropy Ceiling** — repeated values incur an extra end-turn HP penalty.

### UX flow

- Main menu adds: `New Run (Ascension X)` and `Change Ascension`.
- On run start, print active ascension modifiers with short IDs (`A1`, `A2`, ...).
- Add ascension details to `run_summary` and end-of-run log.

### Balance strategy

- Track win rate by ascension level over fixed seeds.
- Keep A1–A3 broadly fair for most decks; A7+ should feel meaningfully hard.
- Avoid “all difficulty = HP inflation”; prefer mechanic diversity (economy, map, intent clarity, constraints).

### Testing checklist

- Unit tests: ascension rule activation by level.
- Unit tests: map/reward/battle hooks apply deterministically under seeded RNG.
- Snapshot tests: same seed differs predictably between `ascension=0` vs `ascension=N`.
- Regression tests: ensure base game (`ascension=0`) behavior remains unchanged.

---

## Risks and mitigations

- **Risk:** sequence state becomes hard to interpret as effects stack.
  - **Mitigation:** keep per-turn transformation logs and effect annotations.
- **Risk:** balancing complexity grows faster than content quality.
  - **Mitigation:** benchmark against fixed seeds and track win rates per archetype.
- **Risk:** UI work forks gameplay logic.
  - **Mitigation:** enforce engine/UI boundary before starting web implementation.
