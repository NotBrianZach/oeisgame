from src.oeisgame import (
    Card,
    has_three_primes_in_first_six,
    initialize_combat_deck,
    no_repeats,
    play_battle,
    prime_score,
    starter_deck,
    starter_enemies,
    start_turn,
)


def test_prime_score_counts_primes():
    assert prime_score([1, 2, 3, 4, 5, 6, 7]) == 4


def test_prime_constraint_works():
    assert has_three_primes_in_first_six([2, 3, 4, 5, 8, 10])
    assert not has_three_primes_in_first_six([1, 4, 6, 8, 9, 11])


def test_no_repeats_constraint():
    assert no_repeats([1, 2, 3])
    assert not no_repeats([1, 2, 2])


def test_battle_produces_history():
    state = play_battle(
        deck=starter_deck(),
        enemy=starter_enemies()[0],
        turns=4,
        enemy_hp=50,
        player_hp=10,
    )

    assert len(state.history) >= 1
    assert len(state.sequence) >= 1


def test_reshuffle_moves_discard_to_draw_pile():
    deck = [Card("A", lambda s: s, cost=1), Card("B", lambda s: s, cost=1)]
    deck_state = initialize_combat_deck(deck)

    first_hand = start_turn(deck_state, hand_size=2)
    assert first_hand == ["A", "B"]

    deck_state.discard_pile.extend(deck_state.hand)
    deck_state.hand.clear()

    second_hand = start_turn(deck_state, hand_size=2)
    assert second_hand == ["A", "B"]


def test_energy_prevents_expensive_card_play():
    enemy = starter_enemies()[0]

    def chooser(_seq, _enemy, _turn, _hand, _energy):
        return 0

    deck = [Card("Too Expensive", lambda s: s + [99], cost=5)]
    state = play_battle(deck=deck, enemy=enemy, turns=1, energy_per_turn=1, chooser=chooser)

    turn = state.history[0]
    assert turn.card_name == "Skip"
    assert turn.note.startswith("Insufficient energy")


def test_invalid_selection_is_guarded():
    enemy = starter_enemies()[0]

    def chooser(_seq, _enemy, _turn, _hand, _energy):
        return 99

    state = play_battle(deck=starter_deck(), enemy=enemy, turns=1, chooser=chooser)

    turn = state.history[0]
    assert turn.card_name == "Skip"
    assert turn.note.startswith("Invalid selection index")
