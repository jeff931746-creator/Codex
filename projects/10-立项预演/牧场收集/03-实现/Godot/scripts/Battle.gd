extends Node2D

const MAIN_SCENE := "res://scenes/Main.tscn"

var player_pos := Vector2(640, 420)
var base_pos := Vector2(640, 600)
var enemies: Array[Dictionary] = []
var projectiles: Array[Dictionary] = []
var wave_index := -1
var spawn_left := 0
var spawn_timer := 0.0
var attack_timer := 0.0
var partner_timer := 0.0
var base_hp := 10
var battle_done := false
var message := ""
var phase_hint := ""


func _ready() -> void:
	_ensure_input_map()
	phase_hint = GameState.get_next_goal_text()
	_start_next_wave()


func _process(delta: float) -> void:
	if battle_done:
		if Input.is_action_just_pressed("attack"):
			get_tree().change_scene_to_file(MAIN_SCENE)
		queue_redraw()
		return

	_update_player(delta)
	_update_spawning(delta)
	_update_attacks(delta)
	_update_projectiles(delta)
	_update_enemies(delta)
	_check_battle_end()
	queue_redraw()


func _update_player(delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	player_pos += direction * 260.0 * delta
	player_pos = player_pos.clamp(Vector2(40, 80), Vector2(1240, 640))


func _update_spawning(delta: float) -> void:
	if spawn_left <= 0:
		return
	spawn_timer -= delta
	if spawn_timer > 0.0:
		return
	var wave := _current_wave()
	spawn_left -= 1
	spawn_timer = 0.55
	enemies.append({
		"pos": Vector2(randf_range(80, 1200), -20),
		"hp": float(wave.get("hp", 20)),
		"max_hp": float(wave.get("hp", 20)),
		"speed": float(wave.get("speed", 45)),
		"damage": int(wave.get("damage", 1))
	})


func _update_attacks(delta: float) -> void:
	attack_timer -= delta
	partner_timer -= delta
	if Input.is_action_pressed("attack") and attack_timer <= 0.0:
		attack_timer = 0.24
		_fire_projectile(player_pos, _aim_direction(), 8.0 + GameState.get_total_power() * 0.5, Color("#f6f0a6"))
	if partner_timer <= 0.0:
		partner_timer = max(0.18, 0.78 - GameState.get_partner_count() * 0.16)
		var target := _nearest_enemy(player_pos)
		if target >= 0:
			var direction: Vector2 = (enemies[target].pos - player_pos).normalized()
			var color := Color("#8ad8ff")
			var damage := 3.0 + GameState.get_total_power() * 0.4
			if "leaf_pup" in GameState.partners:
				color = Color("#62c46e")
				damage += 5.0
			_fire_projectile(player_pos + Vector2(42, -28), direction, damage, color)


func _update_projectiles(delta: float) -> void:
	for projectile in projectiles:
		projectile.pos += projectile.dir * projectile.speed * delta
		projectile.life -= delta
		for enemy in enemies:
			if projectile.pos.distance_to(enemy.pos) < 24.0:
				enemy.hp -= projectile.damage
				projectile.life = 0.0
				break
	projectiles = projectiles.filter(func(projectile): return projectile.life > 0.0)
	enemies = enemies.filter(func(enemy): return enemy.hp > 0.0)


func _update_enemies(delta: float) -> void:
	for enemy in enemies:
		enemy.pos = enemy.pos.move_toward(base_pos, enemy.speed * delta)
		if enemy.pos.distance_to(base_pos) < 30.0:
			base_hp -= int(enemy.damage)
			enemy.hp = 0.0
	enemies = enemies.filter(func(enemy): return enemy.hp > 0.0)
	if base_hp <= 0:
		_end_battle(false)


func _check_battle_end() -> void:
	if battle_done:
		return
	if spawn_left <= 0 and enemies.is_empty():
		if wave_index + 1 >= GameState.get_area(GameState.selected_area_id).get("waves", []).size():
			_end_battle(true)
		else:
			_start_next_wave()


func _start_next_wave() -> void:
	wave_index += 1
	var wave := _current_wave()
	spawn_left = int(wave.get("count", 4))
	spawn_timer = 0.1
	message = "第 %d 波：守住围栏" % (wave_index + 1)


func _current_wave() -> Dictionary:
	var waves: Array = GameState.get_area(GameState.selected_area_id).get("waves", [])
	return waves[min(wave_index, waves.size() - 1)]


func _fire_projectile(origin: Vector2, direction: Vector2, damage: float, color: Color) -> void:
	projectiles.append({
		"pos": origin,
		"dir": direction.normalized(),
		"speed": 540.0,
		"damage": damage,
		"life": 1.2,
		"color": color
	})


func _aim_direction() -> Vector2:
	var target := _nearest_enemy(player_pos)
	if target >= 0:
		return (enemies[target].pos - player_pos).normalized()
	return Vector2.UP


func _nearest_enemy(origin: Vector2) -> int:
	var best := -1
	var best_distance := INF
	for index in range(enemies.size()):
		var distance := origin.distance_squared_to(enemies[index].pos)
		if distance < best_distance:
			best = index
			best_distance = distance
	return best


func _end_battle(victory: bool) -> void:
	battle_done = true
	var summary := GameState.finish_battle(victory)
	message = summary.get("message", "")


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), Color("#1f2a2a"))
	draw_rect(Rect2(base_pos - Vector2(150, 18), Vector2(300, 36)), Color("#8a6a45"))
	draw_string(ThemeDB.fallback_font, Vector2(32, 34), "区域：%s | 据点生命：%d | 战力：%d | 已消耗能量。方向键移动，空格或鼠标左键攻击。" % [
		GameState.get_area(GameState.selected_area_id).get("name", GameState.selected_area_id),
		base_hp,
		GameState.get_total_power()
	], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
	draw_string(ThemeDB.fallback_font, Vector2(32, 62), message, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#d6f6c7"))
	draw_string(ThemeDB.fallback_font, Vector2(32, 90), phase_hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#f3e7a1"))

	draw_circle(player_pos, 20, Color("#72b7ff"))
	_draw_partners()
	for enemy in enemies:
		var health_ratio: float = enemy.hp / max(1.0, enemy.max_hp)
		draw_circle(enemy.pos, 18, Color("#dd6b5a"))
		draw_rect(Rect2(enemy.pos + Vector2(-18, -30), Vector2(36 * health_ratio, 4)), Color("#9cff9c"))
	for projectile in projectiles:
		draw_circle(projectile.pos, 5, projectile.color)

	if battle_done:
		draw_rect(Rect2(Vector2(360, 250), Vector2(560, 150)), Color("#111818cc"))
		draw_string(ThemeDB.fallback_font, Vector2(410, 315), message, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color.WHITE)
		draw_string(ThemeDB.fallback_font, Vector2(410, 355), _end_prompt(), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#d6f6c7"))


func _draw_partners() -> void:
	var index := 0
	for partner_id in GameState.partners.keys():
		var config := GameState.get_partner_config(str(partner_id))
		var offset := Vector2(38 + index * 26, -30 - index * 8)
		var partner_pos := player_pos + offset
		draw_circle(partner_pos, 13, Color(str(config.get("color", "#f0d17a"))))
		draw_string(ThemeDB.fallback_font, partner_pos + Vector2(-26, -18), str(config.get("name", partner_id)), HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color.WHITE)
		index += 1


func _end_prompt() -> String:
	match GameState.demo_phase:
		"reward_1":
			return "按空格或点击鼠标，回牧场查看碎片。"
		"reward_2":
			return "按空格或点击鼠标。完整闭环已经可见。"
	return "按空格或点击鼠标，返回牧场。"


func _ensure_input_map() -> void:
	_add_key_action("move_left", [KEY_A, KEY_LEFT])
	_add_key_action("move_right", [KEY_D, KEY_RIGHT])
	_add_key_action("move_up", [KEY_W, KEY_UP])
	_add_key_action("move_down", [KEY_S, KEY_DOWN])
	_add_key_action("attack", [KEY_SPACE])
	if not InputMap.action_has_event("attack", _mouse_button(MOUSE_BUTTON_LEFT)):
		InputMap.action_add_event("attack", _mouse_button(MOUSE_BUTTON_LEFT))


func _add_key_action(action_name: String, keycodes: Array[int]) -> void:
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)
	for keycode in keycodes:
		var event := _key(keycode)
		if not InputMap.action_has_event(action_name, event):
			InputMap.action_add_event(action_name, event)


func _key(keycode: int) -> InputEventKey:
	var event := InputEventKey.new()
	event.physical_keycode = keycode
	return event


func _mouse_button(button_index: int) -> InputEventMouseButton:
	var event := InputEventMouseButton.new()
	event.button_index = button_index
	return event
