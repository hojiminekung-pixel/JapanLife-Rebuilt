extends Node2D

const SAVE_PATH := "user://japan_life_save.json"
const SAVE_VERSION := 1
const BUILDING_PATH := "res://data/buildings.json"
const DECORATION_PATH := "res://data/decorations.json"
const QUEST_PATH := "res://data/quests.json"
var font: Font
var buildings: Array = []
var decorations: Array = []
var quests: Array = []
var state := {}
var selected := ""
var root_ui: Control
var hud: Label
var grid: GridContainer
var status: Label
var visitor_layer: Control
var elapsed_accumulator := 0.0

func _ready() -> void:
	font = load("res://assets/fonts/NotoSansThai-Regular.ttf")
	buildings = load_json(BUILDING_PATH)
	decorations = load_json(DECORATION_PATH)
	quests = load_json(QUEST_PATH)
	load_game()
	apply_offline_progress()
	build_interface()
	refresh()
	spawn_visitors()

func load_json(path: String) -> Array:
	var text := FileAccess.get_file_as_string(path)
	var parsed = JSON.parse_string(text)
	return parsed if parsed is Array else []

func starter_state() -> Dictionary:
	return {"version": SAVE_VERSION, "gold": 500, "diamonds": 15, "energy": 20, "xp": 0, "level": 1, "reputation": 4, "land": 0, "tiles": {"1_1":{"kind":"road"}, "2_1":{"kind":"road"}, "1_2":{"kind":"tea","level":1,"stored":0.0,"last":Time.get_unix_time_from_system()}, "2_2":{"kind":"home","level":1,"stored":0.0,"last":Time.get_unix_time_from_system()}}, "stats":{"build":2,"road":2,"decorate":0,"upgrade":0,"gold":0}, "claimed":[], "last_seen":Time.get_unix_time_from_system()}

func load_game() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		state = starter_state()
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if parsed is Dictionary and int(parsed.get("version", 0)) <= SAVE_VERSION:
		state = parsed
	else:
		state = starter_state()

func save_game() -> void:
	state["version"] = SAVE_VERSION
	state["last_seen"] = Time.get_unix_time_from_system()
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	f.store_string(JSON.stringify(state))

func apply_offline_progress() -> void:
	var now := Time.get_unix_time_from_system()
	var passed: float = min(28800.0, max(0.0, now - float(state.get("last_seen", now))))
	for tile in state["tiles"].values():
		if tile is Dictionary and tile.get("kind", "") not in ["road", ""]:
			var definition := definition_for(tile["kind"])
			if not definition.is_empty():
				tile["stored"] = min(float(definition.income) * 30.0, float(tile.get("stored", 0.0)) + passed * float(definition.income) / 60.0 * int(tile.get("level", 1)))
	state["last_seen"] = now

func build_interface() -> void:
	root_ui = Control.new()
	root_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(root_ui)
	var backdrop := ColorRect.new()
	backdrop.color = Color("#e8f3e7")
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root_ui.add_child(backdrop)
	var top := PanelContainer.new()
	top.position = Vector2(12, 12); top.size = Vector2(696, 118)
	top.add_theme_stylebox_override("panel", box("#264653", 18))
	root_ui.add_child(top)
	hud = make_label("", 22, Color.WHITE); hud.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	top.add_child(hud)
	status = make_label("", 19, Color("#264653")); status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status.position = Vector2(20, 140); status.size = Vector2(680, 30); root_ui.add_child(status)
	var scroll := ScrollContainer.new(); scroll.position = Vector2(18, 178); scroll.size = Vector2(684, 775); root_ui.add_child(scroll)
	grid = GridContainer.new(); grid.columns = 6; grid.add_theme_constant_override("h_separation", 7); grid.add_theme_constant_override("v_separation", 7); scroll.add_child(grid)
	visitor_layer = Control.new(); visitor_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE; visitor_layer.position = Vector2(20, 180); visitor_layer.size = Vector2(680, 720); root_ui.add_child(visitor_layer)
	var bar := HBoxContainer.new(); bar.position = Vector2(12, 1130); bar.size = Vector2(696, 126); bar.add_theme_constant_override("separation", 8); root_ui.add_child(bar)
	for data in [["🏗️\nสร้าง", "build"], ["🛣️\nถนน", "road"], ["✨\nตกแต่ง", "decor"], ["📜\nภารกิจ", "quests"], ["🗺️\nขยาย", "land"], ["⚙️\nตั้งค่า", "settings"]]:
		var b := make_button(data[0], 17); b.custom_minimum_size = Vector2(108, 120); b.pressed.connect(open_menu.bind(data[1])); bar.add_child(b)

func make_label(text: String, size: int = 18, color := Color.WHITE) -> Label:
	var label := Label.new(); label.text = text; label.add_theme_font_override("font", font); label.add_theme_font_size_override("font_size", size); label.add_theme_color_override("font_color", color); label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER; return label

func box(color: String, radius: int = 12) -> StyleBoxFlat:
	var s := StyleBoxFlat.new(); s.bg_color = Color(color); s.corner_radius_top_left = radius; s.corner_radius_top_right = radius; s.corner_radius_bottom_left = radius; s.corner_radius_bottom_right = radius; s.content_margin_left = 10; s.content_margin_right = 10; s.content_margin_top = 5; s.content_margin_bottom = 5; return s

func make_button(text: String, size: int = 18) -> Button:
	var b := Button.new(); b.text = text; b.add_theme_font_override("font", font); b.add_theme_font_size_override("font_size", size); b.add_theme_stylebox_override("normal", box("#fff7df")); b.add_theme_stylebox_override("hover", box("#f4cf72")); b.add_theme_color_override("font_color", Color("#243b3b")); return b

func refresh() -> void:
	var need: int = int(state["level"]) * 100
	hud.text = "🪙 %d    💎 %d    🍙 %d\nเลเวล %d  XP %d/%d    ⭐ ชื่อเสียง %d" % [state.gold, state.diamonds, state.energy, state.level, state.xp, need, state.reputation]
	status.text = "แตะช่องว่างเพื่อเลือกตำแหน่ง • รายได้พร้อมเก็บ: %d 🪙" % total_stored()
	for child in grid.get_children(): child.queue_free()
	var unlocked := 4 + int(state.land)
	for y in range(6):
		for x in range(6):
			var key := "%d_%d" % [x, y]
			var b := make_button("", 14); b.custom_minimum_size = Vector2(105, 105)
			if x >= unlocked or y >= unlocked:
				b.text = "🔒\nที่ดิน"; b.disabled = true
			elif state.tiles.has(key):
				var tile: Dictionary = state.tiles[key]; var k: String = str(tile.kind)
				if k == "road": b.text = "🛣️\nถนน"; b.add_theme_stylebox_override("normal", box("#b5b9b4"))
				else:
					var d := definition_for(k); b.text = "%s\n%s Lv.%d\n🪙%d" % [symbol_for(k), d.name, tile.level, int(tile.stored)]; b.add_theme_stylebox_override("normal", box(d.color))
			else: b.text = "＋\nว่าง"; b.add_theme_stylebox_override("normal", box("#c8dfbd"))
			b.pressed.connect(tile_pressed.bind(key)); grid.add_child(b)
	save_game()

func tile_pressed(key: String) -> void:
	selected = key
	if state.tiles.has(key) and state.tiles[key].kind != "road":
		show_building_info(key)
	else:
		status.text = "เลือกตำแหน่งแล้ว: แตะเมนูด้านล่างเพื่อสร้าง"

func definition_for(id: String) -> Dictionary:
	for d in buildings + decorations:
		if d.id == id: return d
	return {}

func symbol_for(id: String) -> String:
	var symbols := {"home":"🏠","tea":"🍵","ramen":"🍜","sushi":"🍣","inn":"🏨","shrine":"⛩️","garden":"🌿","museum":"🏛️","market":"🏪","dojo":"🥋","bakery":"🍡","station":"🚉","lantern":"🏮","tree":"🌸","bench":"🪑","torii":"⛩️","pond":"💧"}
	return symbols.get(id, "🏘️")

func open_menu(menu: String) -> void:
	if menu == "road": place_road(); return
	if menu == "build": show_catalog("สร้างอาคาร", buildings, false)
	elif menu == "decor": show_catalog("ของตกแต่ง", decorations, true)
	elif menu == "quests": show_quests()
	elif menu == "land": show_land()
	else: show_settings()

func popup(title: String) -> VBoxContainer:
	var panel := PanelContainer.new(); panel.position = Vector2(35, 250); panel.size = Vector2(650, 700); panel.z_index = 10; panel.add_theme_stylebox_override("panel", box("#fff9ea", 20)); root_ui.add_child(panel)
	var v := VBoxContainer.new(); v.add_theme_constant_override("separation", 9); panel.add_child(v)
	var header := make_label(title, 28, Color("#264653")); v.add_child(header)
	return v

func close_popup(v: VBoxContainer) -> void: v.get_parent().queue_free()

func show_catalog(title: String, data: Array, decoration: bool) -> void:
	var v := popup(title + " — เลือกแล้วแตะช่องว่าง")
	for d in data:
		var b := make_button("%s %s  •  %d 🪙  •  รายได้ %s" % [symbol_for(d.id), d.name, d.cost, "-" if decoration else str(d.income) + "/นาที"], 17)
		b.pressed.connect(place_item.bind(d, decoration, v)); v.add_child(b)
	var close := make_button("ปิด"); close.pressed.connect(close_popup.bind(v)); v.add_child(close)

func place_item(d: Dictionary, decoration: bool, v: VBoxContainer) -> void:
	if selected == "" or state.tiles.has(selected): status.text = "กรุณาแตะช่องว่างก่อน"; return
	if state.gold < int(d.cost): status.text = "เงินไม่พอ"; return
	state.gold -= int(d.cost); state.tiles[selected] = {"kind":d.id, "level":1, "stored":0.0, "last":Time.get_unix_time_from_system()}
	state.stats["decorate" if decoration else "build"] += 1
	if not decoration: gain_xp(int(d.xp)); state.reputation += int(d.get("capacity", 0))
	close_popup(v); refresh()

func place_road() -> void:
	if selected == "" or state.tiles.has(selected): status.text = "เลือกช่องว่างสำหรับถนน"; return
	if state.gold < 10: status.text = "เงินไม่พอ"; return
	state.gold -= 10; state.tiles[selected] = {"kind":"road"}; state.stats.road += 1; refresh()

func show_building_info(key: String) -> void:
	var tile: Dictionary = state.tiles[key]; var d := definition_for(tile.kind); var v := popup(d.name)
	v.add_child(make_label("ระดับ %d/%d • รายได้ %d เหรียญ/นาที\nรายได้ที่สะสม: %d" % [tile.level, d.get("max_level", 1), int(d.get("income",0)) * tile.level, int(tile.stored)], 20, Color("#264653")))
	if float(tile.stored) >= 1:
		var collect := make_button("เก็บรายได้ %d 🪙" % int(tile.stored)); collect.pressed.connect(collect_income.bind(key, v)); v.add_child(collect)
	if int(tile.level) < int(d.get("max_level", 1)):
		var cost := int(d.cost) * int(tile.level)
		var up := make_button("อัปเกรด (%d 🪙)" % cost); up.pressed.connect(upgrade.bind(key, cost, v)); v.add_child(up)
	var close := make_button("ปิด"); close.pressed.connect(close_popup.bind(v)); v.add_child(close)

func collect_income(key: String, v: VBoxContainer) -> void:
	var amount := int(state.tiles[key].stored); state.gold += amount; state.stats.gold += amount; state.tiles[key].stored = 0.0; close_popup(v); refresh()

func upgrade(key: String, cost: int, v: VBoxContainer) -> void:
	if state.gold < cost: status.text = "เงินไม่พอ"; return
	state.gold -= cost; state.tiles[key].level += 1; state.stats.upgrade += 1; gain_xp(20); close_popup(v); refresh()

func gain_xp(amount: int) -> void:
	state.xp += amount
	while state.xp >= state.level * 100:
		state.xp -= state.level * 100; state.level += 1; state.energy += 3; state.diamonds += 1

func show_quests() -> void:
	var v := popup("ภารกิจ")
	for q in quests:
		var done: bool = quest_value(q) >= int(q.target); var claimed: bool = q.id in state.claimed
		var b := make_button(("✅ " if claimed else "📌 ") + q.title + "\n" + q.goal + "  (%d/%d) • รางวัล %d 🪙" % [min(quest_value(q), int(q.target)), q.target, q.reward], 15)
		b.disabled = not done or claimed; b.pressed.connect(claim_quest.bind(q, v)); v.add_child(b)
	var close := make_button("ปิด"); close.pressed.connect(close_popup.bind(v)); v.add_child(close)

func quest_value(q: Dictionary) -> int:
	if q.kind == "rep": return int(state.reputation)
	if q.kind == "level": return int(state.level)
	return int(state.stats.get(q.kind, 0))
func claim_quest(q: Dictionary, v: VBoxContainer) -> void:
	state.claimed.append(q.id); state.gold += int(q.reward); gain_xp(15); close_popup(v); refresh()

func show_land() -> void:
	var v := popup("ขยายที่ดิน")
	var costs := [250, 600, 1200]
	var stage := int(state.land)
	v.add_child(make_label("พื้นที่ปัจจุบัน: %dx%d" % [4 + stage, 4 + stage], 21, Color("#264653")))
	if stage < 3:
		var b := make_button("ขยายเป็น %dx%d (%d 🪙)" % [5 + stage, 5 + stage, costs[stage]]); b.pressed.connect(expand_land.bind(costs[stage], v)); v.add_child(b)
	else: v.add_child(make_label("ขยายครบทุกระยะแล้ว", 20, Color("#264653")))
	var close := make_button("ปิด"); close.pressed.connect(close_popup.bind(v)); v.add_child(close)
func expand_land(cost: int, v: VBoxContainer) -> void:
	if state.gold < cost: status.text = "เงินไม่พอ"; return
	state.gold -= cost; state.land += 1; close_popup(v); refresh()

func show_settings() -> void:
	var v := popup("ตั้งค่า")
	v.add_child(make_label("Japan Life Rebuilt\nเล่นแบบออฟไลน์ • บันทึกอัตโนมัติ", 20, Color("#264653")))
	var save := make_button("บันทึกเกมตอนนี้"); save.pressed.connect(save_game); v.add_child(save)
	var reset := make_button("เริ่มเมืองใหม่"); reset.pressed.connect(reset_game.bind(v)); v.add_child(reset)
	var close := make_button("ปิด"); close.pressed.connect(close_popup.bind(v)); v.add_child(close)
func reset_game(v: VBoxContainer) -> void: state = starter_state(); selected = ""; close_popup(v); refresh()

func total_stored() -> int:
	var total := 0
	for t in state.tiles.values(): total += int(t.get("stored", 0))
	return total
func _process(delta: float) -> void:
	elapsed_accumulator += delta
	if elapsed_accumulator > 1.0:
		elapsed_accumulator = 0.0
		for tile in state.tiles.values():
			if tile.get("kind", "") not in ["road", ""]:
				var d := definition_for(tile.kind)
				tile.stored = min(float(d.income) * 30.0, float(tile.get("stored", 0.0)) + float(d.income) * float(tile.level) / 60.0)
		refresh()
func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_APPLICATION_PAUSED: save_game()
func spawn_visitors() -> void:
	for i in 4:
		var visitor := make_label("🚶", 25); visitor.position = Vector2(20 + i * 150, 420 + (i % 2) * 150); visitor_layer.add_child(visitor)
		var tween := create_tween().set_loops(); tween.tween_property(visitor, "position:x", 560.0 - i * 50, 4.0 + i); tween.tween_property(visitor, "position:x", 20.0 + i * 100, 4.0 + i)
