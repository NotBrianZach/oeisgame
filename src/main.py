from oeisgame import format_battle_log, play_battle, starter_deck, starter_enemies


def main() -> None:
    deck = starter_deck()
    for enemy in starter_enemies():
        state = play_battle(deck=deck, enemy=enemy)
        print(format_battle_log(state, enemy))
        print("-" * 80)


if __name__ == "__main__":
    main()
