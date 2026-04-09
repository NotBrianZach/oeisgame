from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional


Sequence = List[int]
CardChooser = Callable[[Sequence, "Enemy", int, List["Card"], int], Optional[int]]


class Card:
    """A playable sequence operator card."""

    def __init__(self, name: str, apply_fn: Callable[[Sequence], Sequence], cost: int = 1):
        self.name = name
        self._apply_fn = apply_fn
        if cost < 0:
            raise ValueError("cost must be non-negative")
        self.cost = cost

    def apply(self, seq: Sequence) -> Sequence:
        if not seq:
            raise ValueError("Sequence cannot be empty")
        return self._apply_fn(list(seq))

    def __repr__(self) -> str:
        return f"Card({self.name}, cost={self.cost})"


@dataclass
class Enemy:
    name: str
    description: str
    constraint: Callable[[Sequence], bool]
    score: Callable[[Sequence], int]


@dataclass
class CombatDeckState:
    draw_pile: List[Card]
    hand: List[Card]
    discard_pile: List[Card]
    exhaust_pile: List[Card]


@dataclass
class TurnResult:
    turn: int
    card_name: str
    sequence: Sequence
    passed_constraint: bool
    damage_dealt: int
    energy_before: int
    energy_after: int
    hand_before: List[str]
    note: str = ""


@dataclass
class GameState:
    sequence: Sequence
    enemy_hp: int
    player_hp: int
    history: List[TurnResult]
    deck_state: CombatDeckState


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
        Card("Increment", _increment_all, cost=1),
        Card("Double", _double_all, cost=2),
        Card("Append Sum", _append_sum, cost=2),
        Card("Duplicate Last", _duplicate_last, cost=1),
        Card("Fibonacci Kernel", _fibonacci_kernel, cost=2),
        Card("Difference", _difference, cost=1),
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


def initialize_combat_deck(deck: Iterable[Card]) -> CombatDeckState:
    draw_pile = list(deck)
    if not draw_pile:
        raise ValueError("deck must contain at least one card")
    return CombatDeckState(draw_pile=draw_pile, hand=[], discard_pile=[], exhaust_pile=[])


def _draw_cards(deck_state: CombatDeckState, count: int) -> None:
    for _ in range(count):
        if not deck_state.draw_pile and deck_state.discard_pile:
            deck_state.draw_pile = list(deck_state.discard_pile)
            deck_state.discard_pile.clear()
        if not deck_state.draw_pile:
            return
        deck_state.hand.append(deck_state.draw_pile.pop(0))


def start_turn(deck_state: CombatDeckState, hand_size: int) -> List[str]:
    _draw_cards(deck_state, hand_size)
    return [card.name for card in deck_state.hand]


def _default_chooser(
    sequence: Sequence,
    enemy: Enemy,
    turn: int,
    hand: List[Card],
    energy: int,
) -> Optional[int]:
    del sequence, enemy, turn
    for idx, card in enumerate(hand):
        if card.cost <= energy:
            return idx
    return None


def play_card(
    sequence: Sequence,
    enemy: Enemy,
    turn: int,
    deck_state: CombatDeckState,
    energy: int,
    chooser: Optional[CardChooser],
) -> tuple[Sequence, int, str, int, str]:
    hand = deck_state.hand
    if not hand:
        return sequence, energy, "Skip", 0, "No cards in hand"

    choose_fn = chooser or _default_chooser
    selected = choose_fn(list(sequence), enemy, turn, list(hand), energy)
    if selected is None:
        return sequence, energy, "Skip", 0, "No card selected"
    if selected < 0 or selected >= len(hand):
        return sequence, energy, "Skip", 0, f"Invalid selection index {selected}"

    card = hand[selected]
    if card.cost > energy:
        return sequence, energy, "Skip", 0, f"Insufficient energy for {card.name}"

    hand.pop(selected)
    new_sequence = card.apply(sequence)
    remaining_energy = energy - card.cost
    deck_state.discard_pile.append(card)
    damage = max(1, enemy.score(new_sequence))
    return new_sequence, remaining_energy, card.name, damage, ""


def resolve_end_turn(deck_state: CombatDeckState) -> None:
    deck_state.discard_pile.extend(deck_state.hand)
    deck_state.hand.clear()


def play_battle(
    deck: Iterable[Card],
    enemy: Enemy,
    turns: int = 6,
    starting_sequence: Sequence | None = None,
    enemy_hp: int = 25,
    player_hp: int = 10,
    hand_size: int = 3,
    energy_per_turn: int = 3,
    chooser: Optional[CardChooser] = None,
) -> GameState:
    sequence = list(starting_sequence or [1])
    if not sequence:
        raise ValueError("starting_sequence must contain at least one value")

    deck_state = initialize_combat_deck(deck)
    history: List[TurnResult] = []

    for idx in range(turns):
        turn = idx + 1
        hand_names = start_turn(deck_state, hand_size=hand_size)
        energy = energy_per_turn

        sequence, energy_after, card_name, damage, note = play_card(
            sequence=sequence,
            enemy=enemy,
            turn=turn,
            deck_state=deck_state,
            energy=energy,
            chooser=chooser,
        )

        enemy_hp -= damage
        passed = enemy.constraint(sequence)
        if not passed:
            player_hp -= 2

        history.append(
            TurnResult(
                turn=turn,
                card_name=card_name,
                sequence=list(sequence),
                passed_constraint=passed,
                damage_dealt=damage,
                energy_before=energy,
                energy_after=energy_after,
                hand_before=hand_names,
                note=note,
            )
        )

        resolve_end_turn(deck_state)

        if enemy_hp <= 0 or player_hp <= 0:
            break

    return GameState(
        sequence=sequence,
        enemy_hp=enemy_hp,
        player_hp=player_hp,
        history=history,
        deck_state=deck_state,
    )


def format_battle_log(state: GameState, enemy: Enemy) -> str:
    lines = [f"Enemy: {enemy.name} — {enemy.description}"]
    for turn in state.history:
        constraint = "PASS" if turn.passed_constraint else "FAIL"
        lines.append(
            f"Turn {turn.turn}: hand={turn.hand_before} | energy={turn.energy_before}->{turn.energy_after} | "
            f"played={turn.card_name:16} | seq={turn.sequence} | constraint={constraint} | damage={turn.damage_dealt}"
        )
        if turn.note:
            lines.append(f"  note: {turn.note}")
    lines.append(f"Final sequence: {state.sequence}")
    lines.append(f"Enemy HP: {state.enemy_hp}")
    lines.append(f"Player HP: {state.player_hp}")
    lines.append(
        "Deck sizes -> draw: "
        f"{len(state.deck_state.draw_pile)}, discard: {len(state.deck_state.discard_pile)}, "
        f"exhaust: {len(state.deck_state.exhaust_pile)}"
    )
    if state.enemy_hp <= 0 and state.player_hp > 0:
        lines.append("Result: Victory")
    elif state.player_hp <= 0:
        lines.append("Result: Defeat")
    else:
        lines.append("Result: Inconclusive")
    return "\n".join(lines)
