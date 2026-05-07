extends Node

signal state_changed
signal rewards_ready(summary)

const DATA_PATH := "res://configs/demo_data.json"

var data: Dictionary = {}
var energy := 10
var gold := 0
var fragments: Dictionary = {}
var partners: Dictionary = {}
var unlocked_areas: Array[String] = []
var selected_area_id := "meadow"
var last_rewards: Dictionary = {}
var battles_won := 0
var last_growth_message := ""
var demo_phase := "intro"
var last_power_before_growth := 0
var last_power_after_growth := 0

var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	load_data()
	reset_run()


func load_data() -> void:
	var text := FileAccess.get_file_as_string(DATA_PATH)
	if text.is_empty():
		push_error("缺少配置：%s" % DATA_PATH)
		data = {}
		return
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("配置不是有效的 JSON：%s" % DATA_PATH)
		data = {}
		return
	data = parsed


func reset_run() -> void:
	energy = int(data.get("starter_energy", 10))
	gold = 0
	fragments = {}
	partners = {}
	unlocked_areas = ["meadow"]
	last_rewards = {}
	battles_won = 0
	last_growth_message = ""
	demo_phase = "intro"
	last_power_before_growth = get_total_power()
	last_power_after_growth = get_total_power()
	var starter_id := str(data.get("starter_partner", "field_calf"))
	partners[starter_id] = {"level": 1}
	last_power_before_growth = get_total_power()
	last_power_after_growth = get_total_power()
	_emit_state()


func get_area(area_id: String) -> Dictionary:
	return data.get("areas", {}).get(area_id, {})


func get_partner_config(partner_id: String) -> Dictionary:
	return data.get("partners", {}).get(partner_id, {})


func get_total_power() -> int:
	var total := 0
	for partner_id in partners.keys():
		var config := get_partner_config(str(partner_id))
		var level := int(partners[partner_id].get("level", 1))
		total += int(config.get("base_power", 1)) + max(0, level - 1) * int(config.get("growth_power", 1))
	return total


func get_partner_count() -> int:
	return partners.size()


func can_enter_area(area_id: String) -> bool:
	return area_id in unlocked_areas and energy >= int(get_area(area_id).get("energy_cost", 999))


func get_main_action() -> Dictionary:
	match demo_phase:
		"intro":
			return {
				"label": "防守草地牧门",
				"kind": "battle",
				"area_id": str(data.get("demo_steps", {}).get("first_battle_area", "meadow")),
				"enabled": true
			}
		"reward_1":
			return {"label": "查看叶犬碎片", "kind": "advance", "enabled": true}
		"hatch_leaf_pup":
			return {"label": "孵化叶犬", "kind": "hatch", "partner_id": str(data.get("demo_steps", {}).get("first_hatch_partner", "leaf_pup")), "enabled": true}
		"unlock_orchard":
			return {"label": "挑战果园围栏", "kind": "battle", "area_id": str(data.get("demo_steps", {}).get("second_battle_area", "orchard")), "enabled": true}
		"reward_2":
			return {"label": "完成闭环演示", "kind": "advance", "enabled": true}
		"free_loop":
			return {"label": "自由循环：选择已解锁区域", "kind": "none", "enabled": false}
	return {"label": "继续", "kind": "advance", "enabled": true}


func perform_main_action() -> Dictionary:
	var action := get_main_action()
	match str(action.get("kind", "")):
		"battle":
			var area_id := str(action.get("area_id", selected_area_id))
			if begin_battle(area_id):
				return {"scene": "battle"}
		"advance":
			advance_phase()
		"hatch":
			hatch_or_upgrade(str(action.get("partner_id", "")))
	return {"scene": "main"}


func begin_battle(area_id: String) -> bool:
	if not can_enter_area(area_id):
		return false
	selected_area_id = area_id
	energy -= int(get_area(area_id).get("energy_cost", 0))
	if demo_phase == "intro":
		demo_phase = "battle_1"
	elif demo_phase == "unlock_orchard":
		demo_phase = "battle_2"
	_emit_state()
	return true


func finish_battle(victory: bool) -> Dictionary:
	if not victory:
		last_rewards = {
			"victory": false,
			"gold": 0,
			"fragments": {},
			"message": "围栏失守，没有获得碎片。"
		}
		rewards_ready.emit(last_rewards)
		_emit_state()
		return last_rewards

	var area := get_area(selected_area_id)
	var reward_fragments := _roll_fragments(area)
	var demo_steps: Dictionary = data.get("demo_steps", {})
	if demo_phase == "battle_1":
		reward_fragments = demo_steps.get("first_battle_reward", data.get("guided_first_win_fragments", reward_fragments)).duplicate()
	elif demo_phase == "battle_2":
		reward_fragments = demo_steps.get("second_battle_reward", reward_fragments).duplicate()
	var reward_gold := int(area.get("base_gold", 0))
	battles_won += 1
	gold += reward_gold
	for fragment_id in reward_fragments.keys():
		fragments[fragment_id] = int(fragments.get(fragment_id, 0)) + int(reward_fragments[fragment_id])
	var newly_unlocked := refresh_unlocks()
	if demo_phase == "battle_1":
		demo_phase = "reward_1"
	elif demo_phase == "battle_2":
		demo_phase = "reward_2"
	last_rewards = {
		"victory": true,
		"gold": reward_gold,
		"fragments": reward_fragments,
		"unlocked": newly_unlocked,
		"message": _reward_message_for_phase()
	}
	rewards_ready.emit(last_rewards)
	_emit_state()
	return last_rewards


func hatch_or_upgrade(partner_id: String) -> bool:
	var config := get_partner_config(partner_id)
	if config.is_empty():
		return false
	var threshold := int(config.get("hatch_threshold", 5))
	if int(fragments.get(partner_id, 0)) < threshold:
		return false
	last_power_before_growth = get_total_power()
	fragments[partner_id] = int(fragments.get(partner_id, 0)) - threshold
	var partner_name := str(config.get("name", partner_id))
	if partner_id in partners:
		partners[partner_id]["level"] = int(partners[partner_id].get("level", 1)) + 1
		last_growth_message = "%s 升级了。下一场战斗会更强。" % partner_name
	else:
		partners[partner_id] = {"level": 1}
		last_growth_message = "%s 孵化成功。它会立刻加入战斗支援。" % partner_name
	energy += int(data.get("energy_return_on_growth", 2))
	if demo_phase == "hatch_leaf_pup":
		var area_id := str(data.get("demo_steps", {}).get("unlock_after_hatch", "orchard"))
		if not area_id in unlocked_areas:
			unlocked_areas.append(area_id)
			energy += 2
		demo_phase = "unlock_orchard"
	refresh_unlocks()
	last_power_after_growth = get_total_power()
	_emit_state()
	return true


func advance_phase() -> void:
	match demo_phase:
		"reward_1":
			demo_phase = "hatch_leaf_pup"
		"reward_2":
			demo_phase = "free_loop"
	_emit_state()


func hatch_all_available() -> Array[String]:
	var completed: Array[String] = []
	for partner_id in data.get("partners", {}).keys():
		while _can_hatch_or_upgrade(str(partner_id)):
			if hatch_or_upgrade(str(partner_id)):
				completed.append(str(partner_id))
			else:
				break
	return completed


func get_available_growth_ids() -> Array[String]:
	var ids: Array[String] = []
	for partner_id in data.get("partners", {}).keys():
		if _can_hatch_or_upgrade(str(partner_id)):
			ids.append(str(partner_id))
	return ids


func get_next_goal_text() -> String:
	match demo_phase:
		"intro":
			return "防守草地牧门一次。这场胜利会保证拿满叶犬碎片。"
		"battle_1":
			return "守住围栏。战斗奖励会补满叶犬碎片。"
		"reward_1":
			return "叶犬碎片已集满：0/5 -> 5/5。"
		"hatch_leaf_pup":
			return "点击孵化。这一步就是从收集转成成长。"
		"unlock_orchard":
			return "叶犬加入队伍。果园围栏已经开放。"
		"battle_2":
			return "观察叶犬在身边自动支援。这场战斗应该清得更快。"
		"reward_2":
			return "竖切闭环完成。后续奖励会进入自由刷区循环。"
		"free_loop":
			return "自由循环：选择已解锁区域，收集碎片，孵化或升级。"
	return ""


func get_phase_title() -> String:
	match demo_phase:
		"intro":
			return "第 1 步 / 6：防守并获得碎片"
		"battle_1":
			return "第 2 步 / 6：第一场战斗"
		"reward_1":
			return "第 3 步 / 6：收集碎片"
		"hatch_leaf_pup":
			return "第 4 步 / 6：孵化伙伴"
		"unlock_orchard":
			return "第 5 步 / 6：新区解锁"
		"battle_2":
			return "第 6 步 / 6：带叶犬再战"
		"reward_2":
			return "闭环完成"
		"free_loop":
			return "自由收集循环"
	return "牧场循环"


func get_reward_lines() -> Array[String]:
	var lines: Array[String] = []
	if last_rewards.is_empty():
		return lines
	lines.append(str(last_rewards.get("message", "")))
	if bool(last_rewards.get("victory", false)):
		lines.append("金币 +%d" % int(last_rewards.get("gold", 0)))
		for fragment_id in last_rewards.get("fragments", {}).keys():
			var config := get_partner_config(str(fragment_id))
			lines.append("%s碎片 +%d" % [config.get("name", fragment_id), int(last_rewards.get("fragments", {})[fragment_id])])
	return lines


func refresh_unlocks() -> Array[String]:
	var newly_unlocked: Array[String] = []
	for area_id in data.get("areas", {}).keys():
		if area_id in unlocked_areas:
			continue
		if _meets_unlock(get_area(str(area_id)).get("unlock", {})):
			unlocked_areas.append(str(area_id))
			newly_unlocked.append(str(area_id))
			energy += 2
	return newly_unlocked


func _can_hatch_or_upgrade(partner_id: String) -> bool:
	var config := get_partner_config(partner_id)
	if config.is_empty():
		return false
	var threshold := int(config.get("hatch_threshold", 5))
	return int(fragments.get(partner_id, 0)) >= threshold


func _reward_message_for_phase() -> String:
	if demo_phase == "reward_1":
		return "叶犬碎片集满。现在孵化它。"
	if demo_phase == "reward_2":
		return "在叶犬支援下通过了第二场战斗。"
	return "胜利。碎片已经准备好了。"


func get_drop_preview(area_id: String) -> Array:
	var preview := []
	var area := get_area(area_id)
	for partner_id in area.get("drops", []):
		var config := get_partner_config(str(partner_id))
		var threshold := int(config.get("hatch_threshold", 5))
		var owned := int(fragments.get(str(partner_id), 0))
		preview.append({
			"id": str(partner_id),
			"name": str(config.get("name", partner_id)),
			"owned": owned,
			"threshold": threshold,
			"weight": _drop_weight(str(partner_id))
		})
	return preview


func _roll_fragments(area: Dictionary) -> Dictionary:
	var reward := {}
	var rolls := _rng.randi_range(3, 5)
	for i in range(rolls):
		var partner_id := _weighted_pick(area.get("drops", []))
		reward[partner_id] = int(reward.get(partner_id, 0)) + 1
	return reward


func _weighted_pick(drop_ids: Array) -> String:
	var total := 0.0
	for partner_id in drop_ids:
		total += _drop_weight(str(partner_id))
	var cursor := _rng.randf_range(0.0, total)
	for partner_id in drop_ids:
		cursor -= _drop_weight(str(partner_id))
		if cursor <= 0.0:
			return str(partner_id)
	return str(drop_ids.back())


func _drop_weight(partner_id: String) -> float:
	var config := get_partner_config(partner_id)
	var threshold := int(config.get("hatch_threshold", 5))
	var owned := int(fragments.get(partner_id, 0))
	var missing: int = max(0, threshold - owned)
	var weight: float = 1.0 + float(missing) / float(max(1, threshold))
	if missing > 0 and missing <= 2:
		weight += 2.5
	if owned >= threshold:
		weight *= 0.45
	return weight


func _meets_unlock(rule: Dictionary) -> bool:
	match str(rule.get("type", "always")):
		"always":
			return true
		"partner_count":
			return get_partner_count() >= int(rule.get("value", 0))
		"total_power":
			return get_total_power() >= int(rule.get("value", 0))
	return false


func _emit_state() -> void:
	state_changed.emit()
