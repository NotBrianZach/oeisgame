from __future__ import annotations

from typing import List, Optional

from oeisgame import (
    Card,
    Enemy,
    Sequence,
    format_battle_log,
    play_battle,
    recommend_card_by_rollout,
    starter_bosses,
    starter_deck,
    starter_enemies,
)


def cli_chooser(
    sequence: Sequence,
    enemy: Enemy,
    turn: int,
    hand: List[Card],
    energy: int,
) -> Optional[int]:
    recommended = recommend_card_by_rollout(
        sequence=sequence,
        enemy=enemy,
        turn=turn,
        hand=hand,
        energy=energy,
        rollout_steps=3,
    )
    print(f"\nTurn {turn} vs {enemy.name}")
    print(f"Current sequence: {sequence}")
    print(f"Energy: {energy}")
    for idx, card in enumerate(hand):
        marker = " <= rollout pick" if recommended == idx else ""
        print(f"  [{idx}] {card.name} (cost {card.cost}){marker}")

    try:
        raw = input("Choose card index (Enter for rollout recommendation): ").strip()
    except EOFError:
        raw = ""

    if raw == "":
        return recommended

    try:
        return int(raw)
    except ValueError:
        return -1


def main() -> None:
    deck = starter_deck()
    for enemy in starter_enemies():
        state = play_battle(deck=deck, enemy=enemy, chooser=cli_chooser)
        print(format_battle_log(state, enemy))
        print("-" * 80)
    for boss in starter_bosses():
        state = play_battle(deck=deck, enemy=boss, chooser=cli_chooser, enemy_hp=45, turns=8)
        print(format_battle_log(state, boss))
        print("=" * 80)


if __name__ == "__main__":
    main()
