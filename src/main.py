from __future__ import annotations

from typing import List, Optional

from oeisgame import Card, Enemy, Sequence, format_battle_log, play_battle, starter_deck, starter_enemies


def cli_chooser(
    sequence: Sequence,
    enemy: Enemy,
    turn: int,
    hand: List[Card],
    energy: int,
) -> Optional[int]:
    print(f"\nTurn {turn} vs {enemy.name}")
    print(f"Current sequence: {sequence}")
    print(f"Energy: {energy}")
    for idx, card in enumerate(hand):
        print(f"  [{idx}] {card.name} (cost {card.cost})")

    try:
        raw = input("Choose card index (Enter to skip): ").strip()
    except EOFError:
        raw = ""

    if raw == "":
        for idx, card in enumerate(hand):
            if card.cost <= energy:
                return idx
        return None

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


if __name__ == "__main__":
    main()
