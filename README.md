# oeisgame

A very early playable prototype of a roguelike deckbuilder where cards transform integer sequences inspired by OEIS-style pattern play.

## Current prototype (CLI)

This repository now includes a minimal combat loop with:

- A sequence state (starting at `[1]`).
- A starter deck of sequence-operation cards.
- Hand / draw / discard deck flow.
- Per-turn energy and card costs.
- A few enemies with constraints + scoring functions.
- Turn-by-turn battle logging.

## Project layout

- `src/oeisgame.py` — core game engine: cards, enemies, turn phases, scoring, constraints.
- `src/main.py` — command-line runner with card-choice prompt per turn.
- `tests/test_oeisgame.py` — lightweight tests for scoring, constraints, and combat state transitions.

## Run the prototype

```bash
python3 src/main.py
```

Tip: pressing Enter on the prompt uses deterministic fallback (first affordable card), which is useful for quick non-interactive runs.

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

1. Expand play actions to support multi-card turns and card exhaust behavior.
2. Add enemy “anti-cards” that disrupt sequence state.
3. Add map nodes + run progression.
4. Build a basic web UI for sequence visualization.
