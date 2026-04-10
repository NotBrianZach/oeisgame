from src.oeisgame import (
    Card,
    has_three_primes_in_first_six,
    initialize_combat_deck,
    no_repeats,
    play_battle,
    prime_score,
    recommend_card_by_rollout,
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
    assert turn.card_names == ["Skip"]
    assert turn.note.startswith("Insufficient energy")


def test_invalid_selection_is_guarded():
    enemy = starter_enemies()[0]

    def chooser(_seq, _enemy, _turn, _hand, _energy):
        return 99

    state = play_battle(deck=starter_deck(), enemy=enemy, turns=1, chooser=chooser)

    turn = state.history[0]
    assert turn.card_names == ["Skip"]
    assert turn.note.startswith("Invalid selection index")


def test_turn_can_play_multiple_cards():
    enemy = starter_enemies()[0]

    def chooser(_seq, _enemy, _turn, _hand, _energy):
        return 0

    deck = [
        Card("Plus One", lambda s: s + [1], cost=1),
        Card("Plus Two", lambda s: s + [2], cost=1),
        Card("Plus Three", lambda s: s + [3], cost=1),
    ]
    state = play_battle(deck=deck, enemy=enemy, turns=1, energy_per_turn=3, chooser=chooser)

    turn = state.history[0]
    assert turn.card_names == ["Plus One", "Plus Two", "Plus Three"]
    assert turn.energy_after == 0
    assert state.sequence == [1, 1, 2, 3]


def test_exhaust_card_moves_to_exhaust_pile():
    enemy = starter_enemies()[0]

    def chooser(_seq, _enemy, _turn, _hand, _energy):
        return 0

    deck = [Card("One Shot", lambda s: s + [9], cost=1, exhaust_on_play=True)]
    state = play_battle(deck=deck, enemy=enemy, turns=1, energy_per_turn=1, chooser=chooser)

    assert len(state.deck_state.exhaust_pile) == 1
    assert state.deck_state.exhaust_pile[0].name == "One Shot"
    assert state.deck_state.discard_pile == []


def test_rollout_recommends_affordable_high_value_card():
    enemy = starter_enemies()[0]
    hand = [
        Card("Cheap Small", lambda s: s + [2], cost=1),
        Card("Big Growth", lambda s: s + [20], cost=2),
    ]

    selected = recommend_card_by_rollout(
        sequence=[2],
        enemy=enemy,
        turn=1,
        hand=hand,
        energy=2,
        rollout_steps=2,
    )

    assert selected == 1


def test_rollout_returns_none_when_no_affordable_card():
    enemy = starter_enemies()[0]
    hand = [Card("Too Expensive", lambda s: s + [5], cost=4)]

    selected = recommend_card_by_rollout(
        sequence=[1],
        enemy=enemy,
        turn=1,
        hand=hand,
        energy=1,
    )

    assert selected is None
