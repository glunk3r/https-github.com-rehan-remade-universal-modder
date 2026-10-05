class_name GdScenario
extends Node
## Base class for remake acceptance scenarios, run by res://addons/gd_remake/runner.gd.
##
## A scenario script extends this file (prefer the path form, which needs no class cache:
## `extends "res://addons/gd_remake/scenario.gd"`), overrides run() and optionally cases().
## The runner creates a fresh instance per case, sets `params` to that case's dictionary,
## adds it to the tree and awaits run(). Build the world as children of self.

## The current case dictionary (always has "name").
var params: Dictionary = {}
## Failure messages recorded by expect*(); a case passes when this stays empty.
var failures: PackedStringArray = []
## Values recorded with metric(); written to the results JSON.
var metrics: Dictionary = {}

var _held: Dictionary = {}
var _hook: _StepHook


## Emits `stepped` after every other node's _physics_process (highest priority value runs last).
class _StepHook extends Node:
	signal stepped

	func _init() -> void:
		name = "GdrStepHook"
		process_mode = Node.PROCESS_MODE_ALWAYS
		process_physics_priority = 1 << 30

	func _physics_process(_delta: float) -> void:
		stepped.emit()


# _notification runs for every script level, so subclasses cannot accidentally skip this.
func _notification(what: int) -> void:
	if what == NOTIFICATION_ENTER_TREE and _hook == null:
		_hook = _StepHook.new()
		add_child(_hook, false, Node.INTERNAL_MODE_BACK)


## Override to run several cases; each dictionary becomes `params` of one fresh instance.
func cases() -> Array[Dictionary]:
	return [{"name": "default"}]


## Override. May await. Returning ends the case.
func run() -> void:
	expect(false, "%s does not override run()" % get_script().resource_path)


## Await n physics frames: returns once n physics steps (every _physics_process plus the physics
## server step) have completed since the call, at the start of the next step - so press()/expect()
## that follow act before that step's _physics_process. Counts steps while the tree is paused too.
func frames(n: int) -> void:
	if n <= 0:
		return
	for i in n:
		await _hook.stepped
	await get_tree().physics_frame


## Await t seconds of game time (physics-processed timer, honours time scale).
func seconds(t: float) -> void:
	await get_tree().create_timer(t, true, true).timeout


## Press an InputMap action (state is applied immediately and the event is dispatched to the tree).
func press(action: StringName, strength := 1.0) -> void:
	if not InputMap.has_action(action):
		expect(false, "unknown input action '%s'" % action)
		return
	_held[action] = true
	_send_action(action, true, strength)


func release(action: StringName) -> void:
	if not InputMap.has_action(action):
		expect(false, "unknown input action '%s'" % action)
		return
	_held.erase(action)
	_send_action(action, false, 0.0)


## Press, hold for `hold_frames` physics frames, release.
func tap(action: StringName, hold_frames := 2) -> void:
	press(action)
	await frames(hold_frames)
	release(action)


func expect(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)


func expect_near(actual: float, expected: float, tol: float, msg: String) -> void:
	if not (absf(actual - expected) <= tol):
		failures.append("%s: got %s, expected %s +-%s" % [msg, actual, expected, tol])


func expect_eq(actual, expected, msg: String) -> void:
	if typeof(actual) != typeof(expected) and not (_is_number(actual) and _is_number(expected)):
		failures.append("%s: got %s (%s), expected %s (%s)" % [msg, actual, type_string(typeof(actual)), expected, type_string(typeof(expected))])
	elif actual != expected:
		failures.append("%s: got %s, expected %s" % [msg, actual, expected])


func metric(key: String, value) -> void:
	metrics[key] = value


## Instantiate a PackedScene (or a script with a no-argument constructor), add it as a child and return it.
func spawn(scene_path: String) -> Node:
	var res := ResourceLoader.load(scene_path)
	var node: Node = null
	if res is PackedScene:
		node = (res as PackedScene).instantiate()
	elif res is Script and (res as Script).can_instantiate():
		node = (res as Script).new() as Node
	if node == null:
		expect(false, "spawn: cannot instantiate '%s'" % scene_path)
		return null
	add_child(node)
	return node


## Release every action this scenario still holds (the runner also releases all actions between cases).
func release_all() -> void:
	for action in _held.keys():
		_send_action(action, false, 0.0)
	_held.clear()


func _send_action(action: StringName, pressed: bool, strength: float) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = pressed
	ev.strength = strength
	Input.parse_input_event(ev)
	Input.flush_buffered_events()


static func _is_number(v) -> bool:
	return typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT
