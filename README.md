# oeisgame

A very early playable prototype of a roguelike deckbuilder where cards transform integer sequences inspired by OEIS-style pattern play.

## Current prototype (CLI)

This repository now includes a minimal combat loop with:

- A sequence state (starting at `[1]`).
- A starter deck of sequence-operation cards.
- A few enemies with constraints + scoring functions.
- Turn-by-turn battle logging.

## Project layout

- `src/oeisgame.py` — core game engine: cards, enemies, turn loop, scoring, constraints.
- `src/main.py` — simple command-line runner that plays against all starter enemies.
- `tests/test_oeisgame.py` — lightweight tests for scoring, constraints, and simulation sanity.

## Run the prototype

```bash
python3 src/main.py
```

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


## Project roadmap

See `ROADMAP.md` for milestone planning and an actionable sprint backlog.

## Next implementation steps

1. Add hand/draw/discard mechanics (instead of deterministic card cycling).
2. Add per-turn energy and card costs.
3. Add enemy “anti-cards” that disrupt sequence state.
4. Add map nodes + run progression.
5. Build a basic web UI for sequence visualization.
