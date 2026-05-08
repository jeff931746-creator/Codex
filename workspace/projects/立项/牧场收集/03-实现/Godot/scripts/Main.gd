extends Control

const BATTLE_SCENE := "res://scenes/Battle.tscn"

var _root: VBoxContainer
var _phase_label: Label
var _goal_label: Label
var _feedback_box: VBoxContainer
var _partner_box: HBoxContainer
var _action_button: Button
var _debug_box: VBoxContainer


func _ready() -> void:
	var placeholder := get_node_or_null("EditorPlaceholder")
	if placeholder:
		placeholder.queue_free()
	GameState.state_changed.connect(_refresh)
	_build_layout()
	_refresh()


func _build_layout() -> void:
	_root = VBoxContainer.new()
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.add_theme_constant_override("separation", 18)
	_root.offset_left = 96
	_root.offset_top = 56
	_root.offset_right = -96
	_root.offset_bottom = -56
	add_child(_root)

	var title := Label.new()
	title.text = "牧场收集闭环演示"
	title.add_theme_font_size_override("font_size", 34)
	_root.add_child(title)

	_phase_label = Label.new()
	_phase_label.add_theme_font_size_override("font_size", 28)
	_root.add_child(_phase_label)

	_goal_label = Label.new()
	_goal_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_goal_label.add_theme_font_size_override("font_size", 22)
	_root.add_child(_goal_label)

	_action_button = Button.new()
	_action_button.custom_minimum_size = Vector2(0, 64)
	_action_button.add_theme_font_size_override("font_size", 24)
	_action_button.pressed.connect(_perform_main_action)
	_root.add_child(_action_button)

	_feedback_box = VBoxContainer.new()
	_feedback_box.add_theme_constant_override("separation", 10)
	_root.add_child(_feedback_box)

	var partner_title := Label.new()
	partner_title.text = "当前伙伴"
	partner_title.add_theme_font_size_override("font_size", 22)
	_root.add_child(partner_title)

	_partner_box = HBoxContainer.new()
	_partner_box.add_theme_constant_override("separation", 12)
	_root.add_child(_partner_box)

	var debug_title := Label.new()
	debug_title.text = "调试信息：碎片与解锁区域"
	debug_title.add_theme_font_size_override("font_size", 16)
	_root.add_child(debug_title)

	_debug_box = VBoxContainer.new()
	_root.add_child(_debug_box)


func _refresh() -> void:
	_phase_label.text = GameState.get_phase_title()
	_goal_label.text = GameState.get_next_goal_text()

	var action := GameState.get_main_action()
	_action_button.text = str(action.get("label", "继续"))
	_action_button.disabled = not bool(action.get("enabled", true))

	_render_feedback()
	_render_partners()
	_render_debug()


func _perform_main_action() -> void:
	var result := GameState.perform_main_action()
	if result.get("scene", "") == "battle":
		get_tree().change_scene_to_file(BATTLE_SCENE)


func _render_feedback() -> void:
	_clear(_feedback_box)
	match GameState.demo_phase:
		"intro":
			_add_feedback_line("能量 %d | 战力 %d" % [GameState.energy, GameState.get_total_power()], 18)
			_add_feedback_line("本演示会强制走完第一轮收集闭环。", 18)
		"reward_1":
			_add_reward_panel("叶犬碎片", "0/5 -> 5/5", Color("#62c46e"))
		"hatch_leaf_pup":
			_add_hatch_panel("叶犬蛋已准备好", "点击主按钮孵化。它会立刻加入战斗。", Color("#62c46e"))
		"unlock_orchard":
			_add_feedback_line(GameState.last_growth_message, 22)
			_add_feedback_line("战力 %d -> %d" % [GameState.last_power_before_growth, GameState.last_power_after_growth], 24)
			_add_feedback_line("新区解锁：果园围栏", 22)
		"reward_2":
			for line in GameState.get_reward_lines():
				_add_feedback_line(line, 20)
			_add_feedback_line("你已经完成：战斗 -> 收集 -> 孵化 -> 变强后再战。", 22)
		"free_loop":
			_add_free_loop_buttons()
		_:
			for line in GameState.get_reward_lines():
				_add_feedback_line(line, 18)


func _add_reward_panel(title: String, progress: String, color: Color) -> void:
	var box := VBoxContainer.new()
	_feedback_box.add_child(box)
	var icon := ColorRect.new()
	icon.color = color
	icon.custom_minimum_size = Vector2(92, 92)
	box.add_child(icon)
	_add_feedback_line(title, 28)
	_add_feedback_line(progress, 34)
	_add_feedback_line("碎片目标已经完成。下一步是孵化。", 20)


func _add_hatch_panel(title: String, body: String, color: Color) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 16)
	_feedback_box.add_child(row)
	var egg := ColorRect.new()
	egg.color = color
	egg.custom_minimum_size = Vector2(96, 96)
	row.add_child(egg)
	var text_box := VBoxContainer.new()
	row.add_child(text_box)
	var title_label := Label.new()
	title_label.text = title
	title_label.add_theme_font_size_override("font_size", 28)
	text_box.add_child(title_label)
	var body_label := Label.new()
	body_label.text = body
	body_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body_label.add_theme_font_size_override("font_size", 20)
	text_box.add_child(body_label)


func _add_feedback_line(text: String, size: int) -> void:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", size)
	_feedback_box.add_child(label)


func _render_partners() -> void:
	_clear(_partner_box)
	for partner_id in GameState.partners.keys():
		var config := GameState.get_partner_config(str(partner_id))
		var level := int(GameState.partners[partner_id].get("level", 1))
		var power: int = int(config.get("base_power", 1)) + max(0, level - 1) * int(config.get("growth_power", 1))
		var card := VBoxContainer.new()
		card.custom_minimum_size = Vector2(210, 100)
		_partner_box.add_child(card)
		var swatch := ColorRect.new()
		swatch.color = Color(str(config.get("color", "#ffffff")))
		swatch.custom_minimum_size = Vector2(180, 28)
		card.add_child(swatch)
		var name := Label.new()
		name.text = "%s 等级 %d" % [config.get("name", partner_id), level]
		name.add_theme_font_size_override("font_size", 18)
		card.add_child(name)
		var detail := Label.new()
		detail.text = "战力 %d | %s" % [power, config.get("skill", "")]
		card.add_child(detail)


func _render_debug() -> void:
	_clear(_debug_box)
	var status := Label.new()
	var unlocked_names := []
	for area_id in GameState.unlocked_areas:
		unlocked_names.append(GameState.get_area(area_id).get("name", area_id))
	status.text = "能量 %d | 金币 %d | 已解锁 %s | 阶段 %s" % [
		GameState.energy,
		GameState.gold,
		"、".join(unlocked_names),
		GameState.get_phase_title()
	]
	_debug_box.add_child(status)
	var fragments := []
	for partner_id in GameState.data.get("partners", {}).keys():
		var config := GameState.get_partner_config(str(partner_id))
		var threshold := int(config.get("hatch_threshold", 5))
		var count := int(GameState.fragments.get(str(partner_id), 0))
		fragments.append("%s %d/%d" % [config.get("name", partner_id), count, threshold])
	var fragment_label := Label.new()
	fragment_label.text = "碎片：%s" % " | ".join(fragments)
	fragment_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_debug_box.add_child(fragment_label)


func _add_free_loop_buttons() -> void:
	_add_feedback_line("自由循环已经开启。选择下方区域，获得奖励后可孵化或升级伙伴。", 20)
	for area_id in GameState.unlocked_areas:
		var area := GameState.get_area(area_id)
		var button := Button.new()
		button.text = "%s | 能量 %d" % [area.get("name", area_id), area.get("energy_cost", 0)]
		button.disabled = not GameState.can_enter_area(area_id)
		button.pressed.connect(_start_free_battle.bind(area_id))
		_feedback_box.add_child(button)


func _start_free_battle(area_id: String) -> void:
	if GameState.begin_battle(area_id):
		get_tree().change_scene_to_file(BATTLE_SCENE)


func _clear(node: Node) -> void:
	for child in node.get_children():
		child.queue_free()
