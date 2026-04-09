from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List


Sequence = List[int]


class Card:
    """A playable sequence operator card."""

    def __init__(self, name: str, apply_fn: Callable[[Sequence], Sequence]):
        self.name = name
        self._apply_fn = apply_fn

    def apply(self, seq: Sequence) -> Sequence:
        if not seq:
            raise ValueError("Sequence cannot be empty")
        return self._apply_fn(list(seq))

    def __repr__(self) -> str:
        return f"Card({self.name})"


@dataclass
class Enemy:
    name: str
    description: str
    constraint: Callable[[Sequence], bool]
    score: Callable[[Sequence], int]


@dataclass
class TurnResult:
    turn: int
    card_name: str
    sequence: Sequence
    passed_constraint: bool
    damage_dealt: int


@dataclass
class GameState:
    sequence: Sequence
    enemy_hp: int
    player_hp: int
    history: List[TurnResult]


def _append_sum(seq: Sequence) -> Sequence:
    return seq + [sum(seq)]


def _duplicate_last(seq: Sequence) -> Sequence:
    return seq + [seq[-1]]


def _increment_all(seq: Sequence) -> Sequence:
    return [n + 1 for n in seq]


def _double_all(seq: Sequence) -> Sequence:
    return [n * 2 for n in seq]


def _fibonacci_kernel(seq: Sequence) -> Sequence:
    if len(seq) == 1:
        return seq + [seq[-1]]
    return seq + [seq[-1] + seq[-2]]


def _difference(seq: Sequence) -> Sequence:
    if len(seq) < 2:
        return seq
    return [b - a for a, b in zip(seq, seq[1:])]


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def growth_score(seq: Sequence) -> int:
    if len(seq) < 2:
        return 0
    return max(0, seq[-1] - seq[0])


def prime_score(seq: Sequence) -> int:
    return sum(1 for n in seq if _is_prime(n))


def has_three_primes_in_first_six(seq: Sequence) -> bool:
    return sum(1 for n in seq[:6] if _is_prime(n)) >= 3


def no_repeats(seq: Sequence) -> bool:
    return len(set(seq)) == len(seq)


def starter_deck() -> List[Card]:
    return [
        Card("Increment", _increment_all),
        Card("Double", _double_all),
        Card("Append Sum", _append_sum),
        Card("Duplicate Last", _duplicate_last),
        Card("Fibonacci Kernel", _fibonacci_kernel),
        Card("Difference", _difference),
    ]


def starter_enemies() -> List[Enemy]:
    return [
        Enemy(
            name="Exponential Beast",
            description="Maintain strong growth by turn 6.",
            constraint=lambda s: growth_score(s) >= 10,
            score=lambda s: growth_score(s) // 2,
        ),
        Enemy(
            name="Prime Oracle",
            description="At least 3 primes in first 6 terms.",
            constraint=has_three_primes_in_first_six,
            score=prime_score,
        ),
        Enemy(
            name="Entropy Warden",
            description="Avoid repeated values.",
            constraint=no_repeats,
            score=lambda s: len(set(s)),
        ),
    ]


def play_battle(
    deck: Iterable[Card],
    enemy: Enemy,
    turns: int = 6,
    starting_sequence: Sequence | None = None,
    enemy_hp: int = 25,
    player_hp: int = 10,
) -> GameState:
    sequence = list(starting_sequence or [1])
    if not sequence:
        raise ValueError("starting_sequence must contain at least one value")

    cards = list(deck)
    if not cards:
        raise ValueError("deck must contain at least one card")

    history: List[TurnResult] = []

    for idx in range(turns):
        card = cards[idx % len(cards)]
        sequence = card.apply(sequence)

        damage = max(1, enemy.score(sequence))
        enemy_hp -= damage

        passed = enemy.constraint(sequence)
        if not passed:
            player_hp -= 2

        history.append(
            TurnResult(
                turn=idx + 1,
                card_name=card.name,
                sequence=list(sequence),
                passed_constraint=passed,
                damage_dealt=damage,
            )
        )

        if enemy_hp <= 0 or player_hp <= 0:
            break

    return GameState(
        sequence=sequence,
        enemy_hp=enemy_hp,
        player_hp=player_hp,
        history=history,
    )


def format_battle_log(state: GameState, enemy: Enemy) -> str:
    lines = [f"Enemy: {enemy.name} — {enemy.description}"]
    for turn in state.history:
        constraint = "PASS" if turn.passed_constraint else "FAIL"
        lines.append(
            f"Turn {turn.turn}: {turn.card_name:16} -> {turn.sequence} | "
            f"constraint={constraint} | damage={turn.damage_dealt}"
        )
    lines.append(f"Final sequence: {state.sequence}")
    lines.append(f"Enemy HP: {state.enemy_hp}")
    lines.append(f"Player HP: {state.player_hp}")
    if state.enemy_hp <= 0 and state.player_hp > 0:
        lines.append("Result: Victory")
    elif state.player_hp <= 0:
        lines.append("Result: Defeat")
    else:
        lines.append("Result: Inconclusive")
    return "\n".join(lines)
