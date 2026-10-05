extends CanvasLayer
## Variants autoload: swap asset candidates per slot without touching game code.
##
## Candidates live at res://variants/<slot>/<variant>.<ext> (one file per variant; `.import`/`.remap`
## sidecars are folded into the file they describe, so exported builds work too). Without candidates
## a slot falls back to the promoted file res://assets/<slot>.* (first match).
## Active variant: user arg `--variant <slot>=<name>` (repeatable, seeds the choice at launch) >
## in-game choice (F7 cycles slot, F8 cycles variant) > first name sorted.
##   var tex: Texture2D = Variants.load("hero")
##   Variants.bind($Sprite2D, "texture", "hero")   # re-assigned whenever the slot changes

signal changed(slot: String)

const VARIANTS_DIR := "res://variants"
const PROMOTED_DIR := "res://assets"

var _paths: Dictionary = {}  # slot -> {variant name: res path}
var _names: Dictionary = {}  # slot -> PackedStringArray (sorted)
var _choice: Dictionary = {}  # slot -> variant name
var _slot_index := 0
var _bindings: Array[Dictionary] = []  # {node: WeakRef, prop: NodePath, slot: String}
var _label: Label


func _init() -> void:
	layer = 128
	process_mode = Node.PROCESS_MODE_ALWAYS
	rescan()
	_apply_cmdline()


func _ready() -> void:
	_label = Label.new()
	_label.name = "VariantsLabel"
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_label.add_theme_constant_override("outline_size", 4)
	_label.add_theme_color_override("font_outline_color", Color.BLACK)
	_label.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	add_child(_label)
	_label.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT, Control.PRESET_MODE_MINSIZE, 8)
	_refresh_label()


## Re-read res://variants (call after adding candidate files at runtime).
func rescan() -> void:
	_paths.clear()
	_names.clear()
	if not DirAccess.dir_exists_absolute(VARIANTS_DIR):
		return
	for slot in DirAccess.get_directories_at(VARIANTS_DIR):
		var by_name := {}
		for file in _resource_files(VARIANTS_DIR.path_join(slot)):
			var variant := file.get_basename()
			if by_name.has(variant):
				push_warning("Variants: %s/%s has two files named '%s'; using %s" % [VARIANTS_DIR, slot, variant, by_name[variant]])
				continue
			by_name[variant] = VARIANTS_DIR.path_join(slot).path_join(file)
		if by_name.is_empty():
			continue
		var names := PackedStringArray(by_name.keys())
		names.sort()
		_paths[slot] = by_name
		_names[slot] = names
	_slot_index = clampi(_slot_index, 0, maxi(_names.size() - 1, 0))


## {slot: [variant names]} for every slot that has candidates.
func slots() -> Dictionary:
	var out := {}
	for slot in _sorted_slots():
		out[slot] = Array(_names[slot])
	return out


## Active variant name of `slot`, or "" when the slot has no candidates.
func active(slot: String) -> String:
	if not _names.has(slot):
		return ""
	var chosen: String = _choice.get(slot, "")
	return chosen if _paths[slot].has(chosen) else _names[slot][0]


## Path of the resource `load(slot)` returns ("" when there is none).
func path_of(slot: String) -> String:
	if _names.has(slot):
		return _paths[slot][active(slot)]
	if DirAccess.dir_exists_absolute(PROMOTED_DIR):
		for file in _resource_files(PROMOTED_DIR):
			if file.get_basename() == slot:
				return PROMOTED_DIR.path_join(file)
	return ""


## Active candidate of `slot`, else the promoted res://assets/<slot>.*, else null (+ error).
## (Inside this script call it as self.load(): a bare load() is the global ResourceLoader one.)
func load(slot: String) -> Resource:
	var path := path_of(slot)
	if path == "":
		push_error("Variants: no candidates in %s/%s and no %s/%s.*" % [VARIANTS_DIR, slot, PROMOTED_DIR, slot])
		return null
	return ResourceLoader.load(path)


## Make `name` the active variant of `slot`. Returns false for unknown slot/variant.
func set_active(slot: String, variant: String) -> bool:
	if not _names.has(slot) or not _paths[slot].has(variant):
		return false
	if active(slot) == variant:
		_choice[slot] = variant
		return true
	_choice[slot] = variant
	_apply_bindings(slot)
	_refresh_label()
	changed.emit(slot)
	return true


## Assign load(slot) to node.prop now and again whenever the slot's active variant changes.
## `prop` may be an indexed path such as "material:albedo_texture".
func bind(node: Node, prop: String, slot: String) -> void:
	var np := NodePath(prop)
	node.set_indexed(np, self.load(slot))
	_bindings.append({"node": weakref(node), "prop": np, "slot": slot})


func _input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo or _names.is_empty():
		return
	if key.keycode == KEY_F7:
		_slot_index = (_slot_index + 1) % _names.size()
		_refresh_label()
		get_viewport().set_input_as_handled()
	elif key.keycode == KEY_F8:
		var slot: String = _sorted_slots()[_slot_index]
		var names: PackedStringArray = _names[slot]
		set_active(slot, names[(names.find(active(slot)) + 1) % names.size()])
		get_viewport().set_input_as_handled()


func _apply_cmdline() -> void:
	var args := OS.get_cmdline_user_args()
	var specs: PackedStringArray = []
	for i in args.size():
		if args[i] == "--variant" and i + 1 < args.size():
			specs.append(args[i + 1])
		elif args[i].begins_with("--variant="):
			specs.append(args[i].trim_prefix("--variant="))
	for spec in specs:
		var slot := spec.get_slice("=", 0)
		var variant := spec.get_slice("=", 1)
		if not spec.contains("=") or not _names.has(slot) or not _paths[slot].has(variant):
			push_error("Variants: --variant %s: unknown slot/variant (have %s)" % [spec, slots()])
			continue
		_choice[slot] = variant


func _apply_bindings(slot: String) -> void:
	var res: Resource = null
	var loaded := false
	for b in _bindings.duplicate():
		var node: Node = b.node.get_ref()
		if node == null:
			_bindings.erase(b)
			continue
		if b.slot != slot:
			continue
		if not loaded:
			res = self.load(slot)
			loaded = true
		node.set_indexed(b.prop, res)


func _refresh_label() -> void:
	if _label == null:
		return
	_label.visible = not _names.is_empty()
	if _names.is_empty():
		return
	var slot: String = _sorted_slots()[_slot_index]
	var names: PackedStringArray = _names[slot]
	var current := active(slot)
	_label.text = "%s: %s (%d/%d)  F7 slot  F8 variant" % [slot, current, names.find(current) + 1, names.size()]


func _sorted_slots() -> PackedStringArray:
	var keys := PackedStringArray(_names.keys())
	keys.sort()
	return keys


## Resource files of a res:// directory: `.import`/`.remap` sidecars mapped back to the source name,
## `.uid` sidecars and dot files dropped, sorted.
static func _resource_files(dir: String) -> PackedStringArray:
	var seen := {}
	for file in DirAccess.get_files_at(dir):
		if file.begins_with(".") or file.ends_with(".uid"):
			continue
		seen[file.trim_suffix(".import").trim_suffix(".remap")] = true
	var out := PackedStringArray(seen.keys())
	out.sort()
	return out
