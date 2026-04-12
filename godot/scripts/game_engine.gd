extends RefCounted
class_name GameEngine

const DEFAULT_MAX_TURNS := 6
const HAND_SIZE := 3
const TURN_ENERGY := 3

class Card:
	var name: String
	var cost: int
	var rarity: String
	var exhaust_on_play: bool
	var effect: Callable

	func _init(p_name: String, p_cost: int, p_effect: Callable, p_rarity := "common", p_exhaust := false) -> void:
		name = p_name
		cost = p_cost
		effect = p_effect
		rarity = p_rarity
		exhaust_on_play = p_exhaust

	func apply(seq: Array[int]) -> Array[int]:
		return effect.call(seq.duplicate())


class EnemyIntent:
	var name: String
	var description: String
	var effect: Callable

	func _init(p_name: String, p_description: String, p_effect: Callable) -> void:
		name = p_name
		description = p_description
		effect = p_effect

	func apply(seq: Array[int]) -> Array[int]:
		return effect.call(seq.duplicate())


class Enemy:
	var name: String
	var description: String
	var constraint: Callable
	var score: Callable
	var intent_cycle: Array[EnemyIntent] = []
	var encounter_pool := "normal"

	func _init(
		p_name: String,
		p_description: String,
		p_constraint: Callable,
		p_score: Callable,
		p_intent_cycle: Array[EnemyIntent] = [],
		p_pool := "normal",
	) -> void:
		name = p_name
		description = p_description
		constraint = p_constraint
		score = p_score
		intent_cycle = p_intent_cycle
		encounter_pool = p_pool


class MapNode:
	var index: int
	var node_type: String
	var label: String
	var enemy_index := -1
	var next_indices: Array[int] = []

	func _init(p_index: int, p_node_type: String, p_label: String) -> void:
		index = p_index
		node_type = p_node_type
		label = p_label


class CombatState:
	var sequence: Array[int] = [1]
	var enemy_hp := 30
	var player_hp := 12
	var turn := 1
	var max_turns := DEFAULT_MAX_TURNS
	var energy := TURN_ENERGY
	var draw_pile: Array[Card] = []
	var hand: Array[Card] = []
	var discard_pile: Array[Card] = []
	var exhaust_pile: Array[Card] = []
	var log: Array[String] = []
	var finished := false
	var won := false
	var enemy: Enemy
	var telegraphed_intent := ""
	var last_intent := ""


class RunState:
	var seed := 7
	var rng := RandomNumberGenerator.new()
	var node_index := 0
	var nodes: Array[MapNode] = []
	var rewards_taken: Array[String] = []
	var deck: Array[Card] = []
	var player_hp := 12
	var max_hp := 12
	var nodes_cleared := 0
	var ascension_level := 0
	var ascension_modifiers: Array[String] = []


func starter_deck() -> Array[Card]:
	return [
		Card.new("Increment", 1, func(seq: Array[int]) -> Array[int]:
			for i in range(seq.size()):
				seq[i] += 1
			return seq
		),
		Card.new("Double", 1, func(seq: Array[int]) -> Array[int]:
			for i in range(seq.size()):
				seq[i] *= 2
			return seq
		),
		Card.new("Append Sum", 2, func(seq: Array[int]) -> Array[int]:
			var total := 0
			for n in seq:
				total += n
			seq.append(total)
			return seq
		),
		Card.new("Duplicate Last", 1, func(seq: Array[int]) -> Array[int]:
			seq.append(seq[-1])
			return seq
		),
		Card.new("Fibonacci Kernel", 2, func(seq: Array[int]) -> Array[int]:
			if seq.size() == 1:
				seq.append(seq[-1])
			else:
				seq.append(seq[-1] + seq[-2])
			return seq
		),
		Card.new("Difference", 1, func(seq: Array[int]) -> Array[int]:
			if seq.size() < 2:
				return seq
			var out: Array[int] = []
			for i in range(seq.size() - 1):
				out.append(seq[i + 1] - seq[i])
			return out
		),
	]


func starter_enemies() -> Array[Enemy]:
	var trim_tail := EnemyIntent.new(
		"Trim Tail",
		"Remove the last element of your sequence.",
		func(seq: Array[int]) -> Array[int]:
			if seq.size() <= 1:
				return seq
			seq.remove_at(seq.size() - 1)
			return seq
	)
	var negate_tail := EnemyIntent.new(
		"Negate Tail",
		"Flip the sign of the last element.",
		func(seq: Array[int]) -> Array[int]:
			if seq.is_empty():
				return [0]
			seq[-1] = -seq[-1]
			return seq
	)
	var rotate_left := EnemyIntent.new(
		"Rotate Left",
		"Rotate sequence left by one.",
		func(seq: Array[int]) -> Array[int]:
			if seq.size() <= 1:
				return seq
			var first := seq.pop_front()
			seq.append(first)
			return seq
	)

	return [
		Enemy.new(
			"Exponential Beast",
			"Rewards rapid growth in positive values.",
			func(seq: Array[int]) -> bool: return seq.size() >= 2,
			func(seq: Array[int]) -> int:
				var total := 0
				for n in seq:
					total += maxi(0, n)
				return maxi(1, mini(10, total / 8)),
			[trim_tail, negate_tail],
			"normal"
		),
		Enemy.new(
			"Prime Oracle",
			"Penalizes sequences with low prime density.",
			func(seq: Array[int]) -> bool:
				var prime_count := 0
				for n in seq:
					if _is_prime(abs(n)):
						prime_count += 1
				return prime_count >= maxi(1, seq.size() / 3),
			func(seq: Array[int]) -> int:
				var prime_count := 0
				for n in seq:
					if _is_prime(abs(n)):
						prime_count += 1
				return maxi(1, min(10, prime_count + seq.size() / 4)),
			[negate_tail, rotate_left],
			"elite"
		),
		Enemy.new(
			"Entropy Warden",
			"Dislikes repeated values.",
			func(seq: Array[int]) -> bool:
				var seen := {}
				for n in seq:
					if seen.has(n):
						return false
					seen[n] = true
				return true,
			func(seq: Array[int]) -> int:
				var seen := {}
				for n in seq:
					seen[n] = true
				return maxi(1, min(10, seen.size() + seq.size() / 3)),
			[trim_tail, rotate_left],
			"normal"
		),
		Enemy.new(
			"Cathedral of Ratios",
			"Boss that demands both growth and uniqueness.",
			func(seq: Array[int]) -> bool:
				if seq.size() < 3:
					return false
				var seen := {}
				for n in seq:
					if seen.has(n):
						return false
					seen[n] = true
				return true,
			func(seq: Array[int]) -> int:
				if seq.size() < 2:
					return 1
				var growth := maxi(0, seq[-1] - seq[0])
				return maxi(2, mini(12, growth / 3 + seq.size() / 2)),
			[trim_tail, negate_tail, rotate_left],
			"boss"
		),
	]


func initialize_run(seed := 7, ascension_level := 0, nodes := 6) -> RunState:
	var run := RunState.new()
	run.seed = seed
	run.rng.seed = seed
	run.deck = starter_deck()
	run.ascension_level = ascension_level
	run.ascension_modifiers = _ascension_modifiers(ascension_level)
	run.nodes = _generate_map(run.rng, nodes)
	run.player_hp = 12
	run.max_hp = 12
	if ascension_level >= 1:
		run.player_hp = 7
	return run


func encounter_for_node(run: RunState, enemies: Array[Enemy], node_index: int) -> Enemy:
	var node := run.nodes[node_index]
	if node.enemy_index >= 0 and node.enemy_index < enemies.size():
		return enemies[node.enemy_index]
	var pool := node.node_type
	var candidates: Array[Enemy] = []
	for enemy in enemies:
		if enemy.encounter_pool == pool:
			candidates.append(enemy)
	if candidates.is_empty():
		candidates = enemies
	return candidates[run.rng.randi_range(0, candidates.size() - 1)]


func start_combat(run: RunState, enemy: Enemy) -> CombatState:
	var max_turns := DEFAULT_MAX_TURNS
	if run.ascension_level >= 2 and enemy.encounter_pool != "boss":
		max_turns = DEFAULT_MAX_TURNS - 1
	var state := CombatState.new()
	state.enemy = enemy
	state.max_turns = max_turns
	state.player_hp = run.player_hp
	state.sequence = [1]
	state.draw_pile = _shuffle(run.deck.duplicate(), run.rng)
	state.log.append("Encounter: %s" % enemy.name)
	state.log.append("Intent next turn: %s" % _intent_name(enemy, 1))
	start_turn(state)
	return state


func start_turn(state: CombatState) -> void:
	while state.hand.size() < HAND_SIZE and (state.draw_pile.size() > 0 or state.discard_pile.size() > 0):
		if state.draw_pile.is_empty():
			state.draw_pile = _shuffle(state.discard_pile.duplicate())
			state.discard_pile.clear()
		state.hand.append(state.draw_pile.pop_back())
	state.energy = TURN_ENERGY
	state.telegraphed_intent = _intent_name(state.enemy, state.turn)
	state.log.append("Turn %d starts. Intent: %s. Sequence=%s" % [state.turn, state.telegraphed_intent, str(state.sequence)])


func play_card(state: CombatState, hand_index: int) -> void:
	if state.finished:
		return
	if hand_index < 0 or hand_index >= state.hand.size():
		state.log.append("Invalid card choice.")
		return
	var card := state.hand[hand_index]
	if state.energy < card.cost:
		state.log.append("Not enough energy for %s." % card.name)
		return
	state.energy -= card.cost
	state.sequence = card.apply(state.sequence)
	var damage := int(state.enemy.score.call(state.sequence))
	state.enemy_hp = max(0, state.enemy_hp - damage)
	state.log.append("Played %s -> %s (damage %d)" % [card.name, str(state.sequence), damage])
	state.hand.remove_at(hand_index)
	if card.exhaust_on_play:
		state.exhaust_pile.append(card)
	else:
		state.discard_pile.append(card)
	_check_end(state)


func end_turn(state: CombatState) -> void:
	if state.finished:
		return
	for card in state.hand:
		state.discard_pile.append(card)
	state.hand.clear()
	if not state.enemy.constraint.call(state.sequence):
		state.player_hp = max(0, state.player_hp - 2)
		state.log.append("Constraint failed: player takes 2 damage.")
	else:
		state.log.append("Constraint passed.")
	_apply_enemy_intent(state)
	state.turn += 1
	_check_end(state)
	if not state.finished:
		start_turn(state)


func complete_combat(run: RunState, state: CombatState) -> bool:
	run.player_hp = state.player_hp
	if state.won:
		run.nodes_cleared += 1
	return state.won


func reward_choices(run: RunState) -> Array[Dictionary]:
	var options := [
		{"name": "Heal +4", "apply": func(rs: RunState) -> void:
			rs.player_hp = min(rs.max_hp, rs.player_hp + 4)
		},
		{"name": "Add Double", "apply": func(rs: RunState) -> void:
			rs.deck.append(Card.new("Double", 1, func(seq: Array[int]) -> Array[int]:
				for i in range(seq.size()):
					seq[i] *= 2
				return seq
			))
		},
		{"name": "Upgrade Increment", "apply": func(rs: RunState) -> void:
			rs.deck.append(Card.new("Increment+", 0, func(seq: Array[int]) -> Array[int]:
				for i in range(seq.size()):
					seq[i] += 1
				return seq
			))
		},
	]
	if run.ascension_level >= 3:
		return options.slice(0, 2)
	return options


func node_summary(run: RunState) -> String:
	var node := run.nodes[run.node_index]
	return "Node %d/%d (%s)" % [run.node_index + 1, run.nodes.size(), node.node_type]


func next_node_options(run: RunState) -> Array[int]:
	return run.nodes[run.node_index].next_indices


func move_to_next_node(run: RunState, next_index: int) -> void:
	for idx in run.nodes[run.node_index].next_indices:
		if idx == next_index:
			run.node_index = next_index
			return


func _apply_enemy_intent(state: CombatState) -> void:
	if state.enemy.intent_cycle.is_empty():
		return
	var intent := state.enemy.intent_cycle[(state.turn - 1) % state.enemy.intent_cycle.size()]
	state.sequence = intent.apply(state.sequence)
	state.last_intent = intent.name
	state.log.append("Enemy intent %s: %s" % [intent.name, str(state.sequence)])


func _intent_name(enemy: Enemy, turn: int) -> String:
	if enemy.intent_cycle.is_empty():
		return "None"
	return enemy.intent_cycle[(turn - 1) % enemy.intent_cycle.size()].name


func _ascension_modifiers(level: int) -> Array[String]:
	var mods: Array[String] = []
	if level >= 1:
		mods.append("A1 Frail Start: Start at 7/12 HP")
	if level >= 2:
		mods.append("A2 Tighter Clock: Normal and elite combats have one fewer turn")
	if level >= 3:
		mods.append("A3 Lean Rewards: Combat reward choices reduced to two")
	return mods


func _generate_map(rng: RandomNumberGenerator, nodes: int) -> Array[MapNode]:
	var out: Array[MapNode] = []
	for i in range(nodes):
		var node_type := "normal"
		if i == nodes - 1:
			node_type = "boss"
		elif i > 0 and i % 3 == 0:
			node_type = "elite"
		out.append(MapNode.new(i, node_type, "N%d" % i))
	for i in range(nodes - 1):
		out[i].next_indices.append(i + 1)
		if i + 2 < nodes and rng.randf() < 0.5:
			out[i].next_indices.append(i + 2)
	return out


func _check_end(state: CombatState) -> void:
	if state.enemy_hp <= 0:
		state.finished = true
		state.won = true
		state.log.append("Victory!")
	elif state.player_hp <= 0:
		state.finished = true
		state.log.append("Defeat!")
	elif state.turn > state.max_turns:
		state.finished = true
		state.log.append("Out of turns.")


func _shuffle(cards: Array[Card], rng: RandomNumberGenerator = null) -> Array[Card]:
	var local_rng := rng
	if local_rng == null:
		local_rng = RandomNumberGenerator.new()
		local_rng.randomize()
	for i in range(cards.size() - 1, 0, -1):
		var j := local_rng.randi_range(0, i)
		var tmp := cards[i]
		cards[i] = cards[j]
		cards[j] = tmp
	return cards


static func _is_prime(n: int) -> bool:
	if n < 2:
		return false
	if n == 2:
		return true
	if n % 2 == 0:
		return false
	var d := 3
	while d * d <= n:
		if n % d == 0:
			return false
		d += 2
	return true
