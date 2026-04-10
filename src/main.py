from __future__ import annotations

from typing import List, Optional

from oeisgame import (
    Card,
    Enemy,
    RewardOption,
    RunState,
    Sequence,
    format_battle_log,
    play_battle,
    recommend_card_by_rollout,
    run_summary,
    run_single_session,
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
    def reward_cli_chooser(run_state: RunState, options: List[RewardOption]) -> int:
        print("\nReward choice:")
        print(f"HP: {run_state.player_hp}/{run_state.max_hp}")
        for idx, opt in enumerate(options):
            print(f"  [{idx}] {opt.description}")
        try:
            raw = input("Pick reward index (Enter=0): ").strip()
        except EOFError:
            raw = ""
        if raw == "":
            return 0
        try:
            return int(raw)
        except ValueError:
            return 0

    state = run_single_session(
        seed=7,
        nodes=6,
        chooser=cli_chooser,
        reward_chooser=reward_cli_chooser,
    )
    print(f"\nRun seed: {state.seed}")
    for idx, log in enumerate(state.battle_logs, start=1):
        print(f"\n=== Encounter {idx} ===")
        print(log)
    print("\nRewards taken:")
    for reward in state.rewards_taken:
        print(f"- {reward}")
    print(f"Final HP: {state.player_hp}/{state.max_hp}")
    print(run_summary(state))


if __name__ == "__main__":
    main()
