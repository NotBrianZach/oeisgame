# oeisgame

A very early playable prototype of a roguelike deckbuilder where cards transform integer sequences inspired by OEIS-style pattern play.

## Current prototype (CLI)

This repository now includes a minimal combat loop with:

- A sequence state (starting at `[1]`).
- A starter deck of sequence-operation cards.
- Hand / draw / discard deck flow.
- Per-turn energy and card costs.
- Multi-card turns while energy remains.
- Card exhaust behavior for one-shot effects.
- Enemy intent anti-cards with one-turn telegraphing.
- Multi-phase boss encounters with phase-specific intent cycles.
- Run sessions with seeded 5–8 node maps ending in a boss.
- Post-combat reward choices (heal, upgrade, add card).
- Card rarity tiers and weighted reward pulls from a 30+ card library.
- Encounter pools for normal / elite / boss map generation.
- A few enemies with constraints + scoring functions.
- Eight+ enemies total including two multi-phase bosses.
- Turn-by-turn battle logging.
- Interactive built-in web demo with per-turn card choices.
- Branching run-map links with selectable next-node options.
- Relic-lite passive rewards that trigger during battle turns.
- New Game+ style Ascension levels (A1–A3) for harder run modifiers.

## Project layout

- `src/oeisgame.py` — core game engine: cards, enemies, turn phases, scoring, constraints.
- `src/main.py` — command-line runner with card-choice prompt per turn.
- `tests/test_oeisgame.py` — lightweight tests for scoring, constraints, and combat state transitions.

## Run the prototype

```bash
python3 src/main.py
```

## Run the web demo (M5 thin UI)

```bash
python3 src/web.py
```

Then open `http://127.0.0.1:8080`, pick an enemy, and click **Start Battle** to play cards turn-by-turn in the browser.

Tip: pressing Enter on the prompt now uses a short rollout recommendation (3-step lookahead) to pick a card automatically.
During run rewards, pressing Enter takes the first option.
You can also set an Ascension level at run start (Enter defaults to 0).


## Godot migration prototype

The project now includes a larger Godot 4 migration slice under `godot/` with a reusable engine script and a UI scene.

Run it with Godot 4.x by opening `godot/project.godot`.

Current Godot coverage:

- Shared combat engine script (`godot/scripts/game_engine.gd`) with:
  - card definitions and sequence transforms,
  - enemy definitions, encounter pools, and enemy intent cycles,
  - combat deck flow (draw/hand/discard/exhaust),
  - turn lifecycle (`start_turn`, `play_card`, `end_turn`),
  - run-state scaffolding including map nodes, branching node links, and ascension modifiers,
  - post-combat reward choices.
- Main UI scene (`godot/scenes/Main.tscn` + `godot/scripts/main.gd`) with:
  - run/node status display,
  - playable hand and pile counters,
  - telegraphed + applied enemy intent display,
  - post-combat reward picks and next-node branching buttons,
  - combat log output.

Sequence persistence behavior:

- Sequence state is owned by `CombatState.sequence` and carried across turns within a combat.
- New combats intentionally restart sequence at `[1]`, matching the Python prototype's battle-start behavior.

Public asset notes:

- See `godot/assets/ASSET_SOURCES.md` for CC0 packs (Kenney) you can drop in.

## Run tests

```bash
python3 -m pytest -q
```

## Example gameplay ideas represented

- **Cards**: Increment, Double, Append Sum, Duplicate Last, Fibonacci Kernel, Difference.
- **Enemies**:
  - Exponential Beast (growth-focused)
  - Prime Oracle (prime-density constraint)
  - Entropy Warden (anti-repeat constraint)
- **Bosses**:
  - Cathedral of Ratios (growth + uniqueness pressure across phases)
  - Prime Archivist (prime-structure pressure with corruption waves)

## Project roadmap

See `ROADMAP.md` for milestone planning and an actionable sprint backlog.

## Next implementation steps

1. Add map branching choices between node options.
2. Add relic-lite passive rewards with trigger text in logs.
3. Promote web demo into an interactive card-choice UI.

## Roadmap look-ahead

- **M3 completion focus:** richer node events, more meaningful relic-lite rewards, and end-of-run summary stats.
- **M4:** expand card/enemy pools and benchmark balance against fixed seeds.
- **M5:** add a thin web front-end that reuses this same combat/run engine.
