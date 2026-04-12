extends Control

var engine := GameEngine.new()
var run_state: GameEngine.RunState
var combat_state: GameEngine.CombatState
var enemies: Array[GameEngine.Enemy] = []

@onready var run_label: Label = %RunLabel
@onready var stats_label: Label = %StatsLabel
@onready var sequence_label: Label = %SequenceLabel
@onready var pile_label: Label = %PileLabel
@onready var intent_label: Label = %IntentLabel
@onready var log_label: RichTextLabel = %LogLabel
@onready var card_bar: HBoxContainer = %CardBar
@onready var end_turn_button: Button = %EndTurnButton
@onready var reward_bar: HBoxContainer = %RewardBar
@onready var next_node_bar: HBoxContainer = %NextNodeBar

func _ready() -> void:
	enemies = engine.starter_enemies()
	run_state = engine.initialize_run(7, 1, 7)
	_start_current_node_encounter()


func _start_current_node_encounter() -> void:
	var enemy := engine.encounter_for_node(run_state, enemies, run_state.node_index)
	combat_state = engine.start_combat(run_state, enemy)
	reward_bar.visible = false
	next_node_bar.visible = false
	if not end_turn_button.pressed.is_connected(_on_end_turn_pressed):
		end_turn_button.pressed.connect(_on_end_turn_pressed)
	_refresh_ui()


func _on_card_pressed(index: int) -> void:
	if combat_state == null:
		return
	engine.play_card(combat_state, index)
	_refresh_ui()
	if combat_state.finished:
		_on_combat_finished()


func _on_end_turn_pressed() -> void:
	if combat_state == null:
		return
	engine.end_turn(combat_state)
	_refresh_ui()
	if combat_state.finished:
		_on_combat_finished()


func _on_combat_finished() -> void:
	var won := engine.complete_combat(run_state, combat_state)
	if won:
		_show_rewards()
	else:
		run_label.text = "Run failed on %s" % engine.node_summary(run_state)


func _show_rewards() -> void:
	for child in reward_bar.get_children():
		child.queue_free()
	var choices := engine.reward_choices(run_state)
	for choice in choices:
		var b := Button.new()
		b.text = choice.name
		b.pressed.connect(_on_reward_pressed.bind(choice))
		reward_bar.add_child(b)
	reward_bar.visible = true


func _on_reward_pressed(choice: Dictionary) -> void:
	var apply_fn: Callable = choice.apply
	apply_fn.call(run_state)
	run_state.rewards_taken.append(choice.name)
	reward_bar.visible = false
	_show_next_nodes()


func _show_next_nodes() -> void:
	for child in next_node_bar.get_children():
		child.queue_free()
	var options := engine.next_node_options(run_state)
	if options.is_empty():
		run_label.text = "Run complete! Cleared %d nodes." % run_state.nodes_cleared
		next_node_bar.visible = false
		return
	for idx in options:
		var node := run_state.nodes[idx]
		var button := Button.new()
		button.text = "Go to %d (%s)" % [idx + 1, node.node_type]
		button.pressed.connect(_on_next_node_pressed.bind(idx))
		next_node_bar.add_child(button)
	next_node_bar.visible = true


func _on_next_node_pressed(next_idx: int) -> void:
	engine.move_to_next_node(run_state, next_idx)
	_start_current_node_encounter()


func _refresh_ui() -> void:
	if combat_state == null:
		return
	run_label.text = "%s | HP %d/%d | Asc %d" % [
		engine.node_summary(run_state),
		run_state.player_hp,
		run_state.max_hp,
		run_state.ascension_level,
	]
	stats_label.text = "Enemy %s | Turn %d/%d | Energy %d | Enemy HP %d" % [
		combat_state.enemy.name,
		combat_state.turn,
		combat_state.max_turns,
		combat_state.energy,
		combat_state.enemy_hp,
	]
	sequence_label.text = "Sequence: %s" % str(combat_state.sequence)
	pile_label.text = "Draw %d  Hand %d  Discard %d  Exhaust %d" % [
		combat_state.draw_pile.size(),
		combat_state.hand.size(),
		combat_state.discard_pile.size(),
		combat_state.exhaust_pile.size(),
	]
	intent_label.text = "Telegraphed intent: %s | Last applied: %s" % [
		combat_state.telegraphed_intent,
		combat_state.last_intent if combat_state.last_intent != "" else "None",
	]

	for child in card_bar.get_children():
		child.queue_free()
	for i in range(combat_state.hand.size()):
		var card := combat_state.hand[i]
		var button := Button.new()
		button.custom_minimum_size = Vector2(170, 64)
		button.text = "%s\nCost %d" % [card.name, card.cost]
		button.disabled = combat_state.energy < card.cost or combat_state.finished
		button.pressed.connect(_on_card_pressed.bind(i))
		card_bar.add_child(button)

	end_turn_button.disabled = combat_state.finished

	log_label.clear()
	for line in combat_state.log:
		log_label.append_text("• %s\n" % line)
	log_label.scroll_to_line(log_label.get_line_count())
