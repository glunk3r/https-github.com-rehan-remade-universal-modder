extends SceneTree
## gd_remake runner (script main loop). User args go after `--`:
##   godot --headless --path <project> -s res://addons/gd_remake/runner.gd -- \
##         --scenarios res://tests/scenarios/a.gd,res://tests/scenarios/b.gd --out <abs.json> \
##         [--timeout 30] [--case <name>]
##   --timeout: seconds per case (default 30), unless the scenario declares its own (GdScenario.time_limit_s).
##   godot --headless --path <project> -s res://addons/gd_remake/runner.gd -- --boot 120 --out <abs.json>
##   godot --path <project> -s res://addons/gd_remake/runner.gd -- \
##         --grid res://tests/scenarios/a.gd --out <abs.png> [--cell 480x270] [--at 2.0] [--case <name>]
## Prints `GDR_BEGIN <scenario>|<case>` / `GDR_END <scenario>|<case> <status>` around every case,
## writes the results JSON (grid: PNG + "<out>.json") and exits 0 when every case passed, else 1
## (2 for bad invocation). Engine/script errors logged during a case make it `error`.
## Grid cases run concurrently in separate SubViewports (own 2D/3D worlds) but share the global
## Input singleton, so press()/tap() in one cell is seen by all; errors logged during a grid run
## cannot be attributed to one case and mark every case `error`. A case whose run() has not
## returned when `--at` elapses is `timeout`.

const SCENARIO_PATH := "res://addons/gd_remake/scenario.gd"
const Bridge := preload("res://addons/gd_remake/bridge.gd")
const LABEL_H := 24
const MAX_LOGGED := 50


## Collects ERROR / SCRIPT ERROR / SHADER ERROR lines (warnings ignored); thread-safe.
class ErrorLog extends Logger:
	var _mutex := Mutex.new()
	var _lines: PackedStringArray = []
	var _total := 0
	var _script_errors := 0

	func _log_error(function: String, file: String, line: int, code: String, rationale: String,
			_editor_notify: bool, error_type: int, _script_backtraces: Array[ScriptBacktrace]) -> void:
		if error_type == ERROR_TYPE_WARNING:
			return
		var prefix: String = ["ERROR: ", "", "SCRIPT ERROR: ", "SHADER ERROR: "][error_type]
		var text := "%s%s (at %s:%d in %s)" % [prefix, rationale if rationale != "" else code, file, line, function]
		_mutex.lock()
		_total += 1
		if error_type == ERROR_TYPE_SCRIPT:
			_script_errors += 1
		if _lines.size() < MAX_LOGGED:
			_lines.append(text)
		_mutex.unlock()

	func _log_message(_message: String, _error: bool) -> void:
		pass

	## Opaque position; pass to since()/script_errors_since().
	func mark() -> Vector2i:
		_mutex.lock()
		var m := Vector2i(_total, _script_errors)
		_mutex.unlock()
		return m

	func since(m: Vector2i) -> PackedStringArray:
		_mutex.lock()
		var out := _lines.slice(mini(m.x, _lines.size()))
		var dropped := _total - m.x - out.size()
		_mutex.unlock()
		if dropped > 0:
			out.append("(%d more errors not recorded)" % dropped)
		return out

	func script_errors_since(m: Vector2i) -> int:
		_mutex.lock()
		var n := _script_errors - m.y
		_mutex.unlock()
		return n


var _opts: Dictionary = {}
var _log: ErrorLog
var _results: Array[Dictionary] = []
var _time_scale := 1.0


func _initialize() -> void:
	_log = ErrorLog.new()
	OS.add_logger(_log)
	_opts = _parse_args(OS.get_cmdline_user_args())
	Engine.physics_ticks_per_second = int(ProjectSettings.get_setting("physics/common/physics_ticks_per_second", 60))
	_time_scale = Engine.time_scale
	_main.call_deferred()


func _main() -> void:
	var code := 2
	if _opts.has("scenarios"):
		code = await _run_scenarios()
	elif _opts.has("boot"):
		code = await _run_boot()
	elif _opts.has("grid"):
		code = await _run_grid()
	else:
		printerr("gd_remake runner: expected --scenarios <res paths> | --boot <frames> | --grid <res path>, plus --out <abs path>")
	quit(code)


func _run_scenarios() -> int:
	var timeout := float(_opts.get("timeout", "30"))
	var only: String = _opts.get("case", "")
	for raw in str(_opts.scenarios).split(",", false):
		var path := raw.strip_edges()
		var loaded := _load_scenario(path)
		if loaded.has("error"):
			continue
		var matched := false
		for c in loaded.cases:
			if only != "" and c.name != only:
				continue
			matched = true
			_results.append(await _run_case(loaded.script, path, c, timeout))
		if not matched:
			_record_error(path, only, "no case named '%s' (have %s)" % [only, ", ".join(loaded.cases.map(func(c): return c.name))])
	if _results.is_empty():
		_record_error(str(_opts.scenarios), "", "no scenarios given")
	_write_json(_opts.get("out", ""), _results)
	return _exit_code()


func _run_case(script: Script, path: String, case: Dictionary, timeout: float) -> Dictionary:
	var entry := _entry(path, case.name)
	_write_json(_opts.get("out", ""), _results + [entry])  # survives a crash or quit() mid-case
	print("GDR_BEGIN %s|%s" % [path, case.name])
	var before := root.get_children()
	var mark := _log.mark()
	var t0 := Time.get_ticks_msec()
	var node: Node = script.new()
	node.name = "Scenario"
	node.set("params", case.duplicate(true))
	root.add_child(node)
	current_scene = node
	var limit := timeout
	var own := float(node.call("time_limit_s")) if node.has_method("time_limit_s") else 0.0
	if own > 0.0:
		limit = own  # the scenario's declared limit for its cases (GdScenario.time_limit_s)
	var state := {"done": false}
	_drive(node, state)
	var timed_out := false
	while not state.done:
		if _log.script_errors_since(mark) > 0:
			break
		if (Time.get_ticks_msec() - t0) >= limit * 1000.0:
			timed_out = true
			break
		await process_frame
	entry.duration_ms = Time.get_ticks_msec() - t0
	_finish(entry, node, _log.since(mark), timed_out, "run() did not return within %ss" % limit)
	print("GDR_END %s|%s %s" % [path, case.name, entry.status])
	await _cleanup(before)
	return entry


func _run_boot() -> int:
	var frames := int(_opts.boot)
	var entry := _entry("boot", "main")
	_write_json(_opts.get("out", ""), [entry])
	print("GDR_BEGIN boot|main")
	var before := root.get_children()
	var mark := _log.mark()
	var t0 := Time.get_ticks_msec()
	var main_path := str(ProjectSettings.get_setting("application/run/main_scene", ""))
	entry.metrics = {"frames": frames, "main_scene": main_path}
	if main_path == "" or not ResourceLoader.exists(main_path):
		entry.status = "fail"
		entry.message = "main scene missing: '%s'" % main_path
		entry.failures = [entry.message]
	else:
		var scene := ResourceLoader.load(main_path) as PackedScene
		var inst: Node = scene.instantiate() if scene else null
		if inst == null:
			entry.message = "cannot load/instantiate main scene '%s'" % main_path
			entry.failures = [entry.message] + Array(_log.since(mark))
		else:
			root.add_child(inst)
			current_scene = inst
			for i in maxi(frames, 0):
				await process_frame
			var errors := _log.since(mark)
			entry.failures = Array(errors)
			entry.status = "error" if errors.size() > 0 else "pass"
			entry.message = errors[0] if errors.size() > 0 else ""
	entry.duration_ms = Time.get_ticks_msec() - t0
	print("GDR_END boot|main %s" % entry.status)
	_results.append(entry)
	_write_json(_opts.get("out", ""), _results)
	await _cleanup(before)
	return _exit_code()


func _run_grid() -> int:
	var out := str(_opts.get("out", "")).replace("\\", "/")
	var path := str(_opts.grid).strip_edges()
	if DisplayServer.get_name() == "headless":
		printerr("gd_remake runner: --grid needs rendering; run without --headless")
		_record_error(path, "", "--grid cannot run headless (no rendering)")
		_write_json(out + ".json" if out != "" else "", _results)
		return 1
	var cell := _parse_size(str(_opts.get("cell", "480x270")))
	var at := float(_opts.get("at", "2.0"))
	var only: String = _opts.get("case", "")
	var loaded := _load_scenario(path)
	if loaded.has("error"):
		_write_json(out + ".json" if out != "" else "", _results)
		return 1
	var cases: Array = loaded.cases.filter(func(c): return only == "" or c.name == only)
	if cases.is_empty():
		_record_error(path, only, "no case named '%s'" % only)
		_write_json(out + ".json" if out != "" else "", _results)
		return 1

	var cols := ceili(sqrt(cases.size()))
	var rows := ceili(cases.size() / float(cols))
	var canvas := SubViewport.new()
	canvas.size = Vector2i(cols * cell.x, rows * (cell.y + LABEL_H))
	canvas.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	var bg := ColorRect.new()
	bg.color = Color(0.08, 0.08, 0.08)
	bg.size = canvas.size
	canvas.add_child(bg)
	var grid := GridContainer.new()
	grid.columns = cols
	grid.add_theme_constant_override("h_separation", 0)
	grid.add_theme_constant_override("v_separation", 0)
	canvas.add_child(grid)
	root.add_child(canvas)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	var usable := DisplayServer.screen_get_usable_rect().size * 0.9
	var fit := minf(1.0, minf(usable.x / canvas.size.x, usable.y / canvas.size.y))
	root.size = Vector2i(maxi(int(canvas.size.x * fit), 64), maxi(int(canvas.size.y * fit), 64))
	var view := TextureRect.new()
	view.texture = canvas.get_texture()
	view.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	view.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	root.add_child(view)
	view.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	var runs: Array[Dictionary] = []
	var mark := _log.mark()
	var t0 := Time.get_ticks_msec()
	for c in cases:
		var box := VBoxContainer.new()
		box.add_theme_constant_override("separation", 0)
		var head := HBoxContainer.new()
		head.custom_minimum_size = Vector2(cell.x, LABEL_H)
		var name_label := _label(" " + c.name, Color.WHITE)
		var fail_label := _label("", Color(1.0, 0.25, 0.25))
		fail_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		fail_label.clip_text = true
		head.add_child(name_label)
		head.add_child(fail_label)
		var holder := SubViewportContainer.new()
		holder.custom_minimum_size = cell
		holder.stretch = true
		var vp := SubViewport.new()
		vp.size = cell
		vp.own_world_3d = true
		vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		holder.add_child(vp)
		box.add_child(head)
		box.add_child(holder)
		grid.add_child(box)
		print("GDR_BEGIN %s|%s" % [path, c.name])
		var node: Node = loaded.script.new()
		node.name = "Scenario"
		node.set("params", c.duplicate(true))
		vp.add_child(node)
		var state := {"done": false}
		runs.append({"case": c, "node": node, "state": state, "label": fail_label})
		_drive(node, state)
	while (Time.get_ticks_msec() - t0) < at * 1000.0 and runs.any(func(r): return not r.state.done):
		await process_frame
	var errors := _log.since(mark)
	if errors.size() > 0:
		errors.insert(0, "errors logged while cases ran concurrently (not attributable to one case):")
	for r in runs:
		var entry := _entry(path, r.case.name)
		entry.duration_ms = Time.get_ticks_msec() - t0
		_finish(entry, r.node, errors, not r.state.done, "still running at capture (--at %ss)" % at)
		if entry.status != "pass":
			r.label.text = " FAIL: " + str(entry.message)
		print("GDR_END %s|%s %s" % [path, r.case.name, entry.status])
		_results.append(entry)
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var img := canvas.get_texture().get_image()
	if out != "":
		DirAccess.make_dir_recursive_absolute(out.get_base_dir())
	var err := img.save_png(out) if out != "" and img != null else ERR_INVALID_PARAMETER
	if err != OK:
		printerr("gd_remake runner: cannot save grid PNG to '%s': %s" % [out, error_string(err)])
	_write_json(out + ".json" if out != "" else "", _results)
	return _exit_code() if err == OK else 1


## Loads and validates a scenario script; on failure records an `error` result and returns {"error": msg}.
func _load_scenario(path: String) -> Dictionary:
	print("GDR_BEGIN %s|load" % path)
	var mark := _log.mark()
	var msg := ""
	var script: Script = null
	var cases: Array[Dictionary] = []
	if not ResourceLoader.exists(path):
		msg = "no such script: %s" % path
	else:
		script = ResourceLoader.load(path) as Script
		if script == null or not script.can_instantiate():
			var errs := _log.since(mark)
			msg = "script failed to load: %s" % (errs[0] if errs.size() > 0 else path)
			if msg.contains("Could not find base class"):
				msg += " (no global class cache: run `godot --headless --path <project> --import` first, or use extends \"%s\")" % SCENARIO_PATH
		elif not _is_scenario(script):
			msg = "%s is not a GdScenario (use extends \"%s\")" % [path, SCENARIO_PATH]
		else:
			var probe: Node = script.new()
			var listed = probe.call("cases")
			probe.free()
			if typeof(listed) != TYPE_ARRAY or listed.is_empty():
				msg = "cases() must return a non-empty Array of Dictionaries"
			else:
				for i in listed.size():
					if typeof(listed[i]) != TYPE_DICTIONARY:
						msg = "cases()[%d] is not a Dictionary" % i
						break
					var c: Dictionary = listed[i].duplicate(true)
					c.name = str(c.get("name", "case%d" % i))
					cases.append(c)
			if msg == "" and _log.since(mark).size() > 0:
				msg = "error while listing cases: %s" % _log.since(mark)[0]
	if msg != "":
		print("GDR_END %s|load error" % path)
		_record_error(path, "load", msg, _log.since(mark))
		return {"error": msg}
	print("GDR_END %s|load pass" % path)
	return {"script": script, "cases": cases}


func _drive(node: Node, state: Dictionary) -> void:
	var scenario = node
	await scenario.run()
	state.done = true


## Fills status/message/failures/metrics of `entry` from the scenario node and logged errors.
func _finish(entry: Dictionary, node: Node, errors: PackedStringArray, unfinished: bool, unfinished_msg: String) -> void:
	var failures: Array = Array(node.get("failures")) if is_instance_valid(node) else []
	entry.metrics = Bridge.encode(node.get("metrics")) if is_instance_valid(node) else {}
	if errors.size() > 0:
		entry.status = "error"
		entry.message = errors[1] if errors.size() > 1 and errors[0].ends_with(":") else errors[0]
		failures.append_array(Array(errors))
	elif unfinished:
		entry.status = "timeout"
		entry.message = unfinished_msg
		failures.append(unfinished_msg)
	elif failures.size() > 0:
		entry.status = "fail"
		entry.message = failures[0]
	else:
		entry.status = "pass"
		entry.message = ""
	entry.failures = failures


## Frees everything added under root since `before` (cancelling pending coroutines), releases
## inputs, unpauses and restores the time scale.
func _cleanup(before: Array[Node]) -> void:
	current_scene = null
	for ch in root.get_children():
		if not before.has(ch):
			if ch.has_method("release_all"):
				ch.call("release_all")
			ch.free()
	for action in InputMap.get_actions():
		if Input.is_action_pressed(action):
			Input.action_release(action)
	paused = false
	Engine.time_scale = _time_scale
	Engine.physics_ticks_per_second = int(ProjectSettings.get_setting("physics/common/physics_ticks_per_second", 60))
	await physics_frame


func _entry(scenario: String, case_name: String) -> Dictionary:
	return {"scenario": scenario, "case": case_name, "status": "error",
		"message": "runner did not finish this case (engine crash or the game called quit())",
		"failures": [], "metrics": {}, "duration_ms": 0}


func _record_error(scenario: String, case_name: String, msg: String, extra := PackedStringArray()) -> void:
	var entry := _entry(scenario, case_name)
	entry.message = msg
	entry.failures = Array(extra) if extra.size() > 0 else [msg]
	_results.append(entry)


func _write_json(out: String, results: Array) -> void:
	if out == "":
		return
	out = out.replace("\\", "/")
	DirAccess.make_dir_recursive_absolute(out.get_base_dir())
	var f := FileAccess.open(out, FileAccess.WRITE)
	if f == null:
		printerr("gd_remake runner: cannot write '%s': %s" % [out, error_string(FileAccess.get_open_error())])
		return
	f.store_string(JSON.stringify({"godot": Bridge.godot_version(), "results": results}, "  ", false))
	f.close()


func _exit_code() -> int:
	var counts := {}
	for r in _results:
		counts[r.status] = counts.get(r.status, 0) + 1
	print("GDR_SUMMARY %s" % " ".join(counts.keys().map(func(k): return "%s=%d" % [k, counts[k]])))
	return 0 if not _results.is_empty() and counts.get("pass", 0) == _results.size() else 1


func _is_scenario(script: Script) -> bool:
	var s := script
	while s != null:
		if s.resource_path == SCENARIO_PATH:
			return true
		s = s.get_base_script()
	return false


func _label(text: String, color: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.add_theme_color_override("font_color", color)
	l.add_theme_font_size_override("font_size", 14)
	return l


static func _parse_size(s: String) -> Vector2i:
	var parts := s.to_lower().split("x")
	if parts.size() == 2 and parts[0].is_valid_int() and parts[1].is_valid_int():
		return Vector2i(maxi(parts[0].to_int(), 16), maxi(parts[1].to_int(), 16))
	return Vector2i(480, 270)


## `--key value`, `--key=value` and bare `--flag` (value "") forms; the last occurrence wins.
static func _parse_args(args: PackedStringArray) -> Dictionary:
	var o := {}
	var i := 0
	while i < args.size():
		var a := args[i]
		if a.begins_with("--"):
			var key := a.substr(2)
			var value := ""
			var eq := key.find("=")
			if eq >= 0:
				value = key.substr(eq + 1)
				key = key.left(eq)
			elif i + 1 < args.size() and not args[i + 1].begins_with("--"):
				i += 1
				value = args[i]
			o[key] = value
		i += 1
	return o
