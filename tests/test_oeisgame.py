from src.oeisgame import (
    has_three_primes_in_first_six,
    no_repeats,
    play_battle,
    prime_score,
    starter_deck,
    starter_enemies,
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
