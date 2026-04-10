from src.oeisgame import (
    Card,
    Enemy,
    EnemyIntent,
    generate_run_map,
    has_three_primes_in_first_six,
    initialize_combat_deck,
    no_repeats,
    play_battle,
    prime_score,
    recommend_card_by_rollout,
    run_single_session,
    starter_bosses,
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
    enemy = Enemy(
        name="Training Dummy",
        description="No enemy intent effects.",
        constraint=lambda s: True,
        score=lambda s: len(s),
    )

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


def test_enemy_intents_cycle_deterministically():
    enemy = starter_enemies()[0]
    state = play_battle(deck=starter_deck(), enemy=enemy, turns=2)

    assert state.history[0].enemy_intent == "Growth Suppressor"
    assert state.history[0].telegraphed_intent == "Tail Shear"
    assert state.history[1].enemy_intent == "Tail Shear"
    assert state.history[1].telegraphed_intent == "Predator Momentum"


def test_enemy_intent_effect_applies_after_player_turn():
    enemy = Enemy(
        name="Truncator",
        description="Truncates sequence",
        constraint=lambda s: True,
        score=lambda s: len(s),
        intent_cycle=[
            EnemyIntent(
                name="Clip",
                kind="disrupt",
                description="Remove latest term",
                apply_effect=lambda s: s[:-1] if len(s) > 1 else s,
            )
        ],
    )
    deck = [Card("Plus Nine", lambda s: s + [9], cost=1)]
    state = play_battle(
        deck=deck,
        enemy=enemy,
        turns=1,
        starting_sequence=[1],
        energy_per_turn=1,
    )

    assert state.history[0].enemy_intent == "Clip"
    assert "Enemy intent Clip [disrupt]" in state.history[0].note
    assert state.sequence == [1]


def test_starter_enemies_have_multi_type_intent_tables():
    for enemy in starter_enemies():
        assert enemy.intent_cycle is not None
        kinds = {intent.kind for intent in enemy.intent_cycle}
        assert len(kinds) >= 2


def test_starter_bosses_have_phases_and_boss_flag():
    bosses = starter_bosses()
    assert len(bosses) >= 2
    for boss in bosses:
        assert boss.is_boss
        assert boss.phases is not None
        assert len(boss.phases) >= 2


def test_boss_phase_transitions_and_telegraphs():
    boss = starter_bosses()[0]
    state = play_battle(deck=starter_deck(), enemy=boss, turns=4, enemy_hp=999)

    assert state.history[0].enemy_phase == "Sanctum Gate"
    assert state.history[0].enemy_intent == "Choir of Noise"
    assert state.history[1].enemy_phase == "Sanctum Gate"
    assert state.history[1].enemy_intent == "Pillar Shear"
    assert state.history[2].enemy_phase == "Ratio Sermon"
    assert state.history[2].enemy_intent == "Suppressive Litany"
    assert state.history[3].enemy_phase == "Ratio Sermon"
    assert state.history[3].enemy_intent == "Escalation Canticle"


def test_boss_phase_penalty_applies():
    boss = starter_bosses()[0]
    state = play_battle(
        deck=starter_deck(),
        enemy=boss,
        turns=1,
        player_hp=10,
        starting_sequence=[1],
        energy_per_turn=0,
        enemy_hp=999,
    )

    # turn 1 is in Sanctum Gate phase with a fail penalty of 2.
    assert state.player_hp <= 8


def test_generate_run_map_has_final_boss_node():
    generated = generate_run_map(seed=5, nodes=6)
    assert len(generated) == 6
    assert generated[-1].node_type == "boss"
    assert generated[-1].enemy is not None
    assert generated[-1].enemy.is_boss


def test_run_session_progresses_and_records_rewards():
    state = run_single_session(seed=11, nodes=6)
    assert state.node_position >= 1
    assert len(state.battle_logs) >= 1
    assert len(state.rewards_taken) >= 1


def test_run_reward_upgrade_reduces_cost():
    def pick_upgrade(_run_state, options):
        for idx, option in enumerate(options):
            if option.kind == "upgrade":
                return idx
        return 0

    state = run_single_session(seed=2, nodes=5, reward_chooser=pick_upgrade)
    upgraded_cards = [card for card in state.deck if card.name.endswith("+")]
    assert len(upgraded_cards) >= 1
