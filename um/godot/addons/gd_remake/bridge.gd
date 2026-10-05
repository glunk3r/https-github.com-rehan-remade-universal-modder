extends Node
## GdBridge autoload: newline-delimited JSON control socket for agents.
##
## Inactive unless the user arg `--gd-bridge=<port>` (after `--`) or env `GD_BRIDGE_PORT` is set.
## Listens on 127.0.0.1 only. Request `{"id":1,"cmd":"tree","args":{...}}`, response
## `{"id":1,"ok":true,"result":...}` or `{"id":1,"ok":false,"error":"..."}`.
## Commands: ping, tree, get, set, call, eval, action, key, frames, wait, screenshot, quit.
## Slow commands (frames, wait, call of a coroutine, screenshot) answer later without blocking
## other requests; responses may therefore arrive out of request order (match on "id").

var port := 0

var _server: TCPServer
var _clients: Array[Dictionary] = []


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	port = _requested_port()
	if port <= 0:
		set_process(false)
		return
	_server = TCPServer.new()
	var err := _server.listen(port, "127.0.0.1")
	if err != OK:
		push_error("GdBridge: cannot listen on 127.0.0.1:%d (%s)" % [port, error_string(err)])
		_server = null
		set_process(false)
		return
	print("GdBridge: listening on 127.0.0.1:%d" % port)


func _exit_tree() -> void:
	for c in _clients:
		(c.peer as StreamPeerTCP).disconnect_from_host()
	_clients.clear()
	if _server:
		_server.stop()


func _process(_delta: float) -> void:
	while _server.is_connection_available():
		var peer := _server.take_connection()
		peer.set_no_delay(true)
		_clients.append({"peer": peer, "buf": PackedByteArray()})
	for c in _clients.duplicate():
		var peer: StreamPeerTCP = c.peer
		peer.poll()
		var status := peer.get_status()
		if status == StreamPeerTCP.STATUS_CONNECTING:
			continue
		var avail := peer.get_available_bytes() if status == StreamPeerTCP.STATUS_CONNECTED else 0
		if avail > 0:
			var got := peer.get_partial_data(avail)
			if got[0] == OK:
				var acc: PackedByteArray = c.buf
				acc.append_array(got[1])
				c.buf = acc
		while true:
			var buf: PackedByteArray = c.buf
			var nl := buf.find(10)
			if nl < 0:
				break
			var line := buf.slice(0, nl).get_string_from_utf8().strip_edges()
			c.buf = buf.slice(nl + 1)
			if line != "":
				_handle(peer, line)
		if status != StreamPeerTCP.STATUS_CONNECTED:
			_clients.erase(c)


func _handle(peer: StreamPeerTCP, line: String) -> void:
	var req = JSON.parse_string(line)
	if typeof(req) != TYPE_DICTIONARY:
		_send(peer, {"id": null, "ok": false, "error": "request is not a JSON object: " + line.left(200)})
		return
	var id = req.get("id")
	if typeof(id) == TYPE_FLOAT and is_finite(id) and id == floorf(id):
		id = int(id)
	var args = req.get("args", {})
	if args == null:
		args = {}
	if typeof(args) != TYPE_DICTIONARY:
		_send(peer, {"id": id, "ok": false, "error": "args must be a JSON object"})
		return
	var cmd := str(req.get("cmd", ""))
	var out: Dictionary = await _dispatch(cmd, args)
	out["id"] = id
	_send(peer, out)
	if cmd == "quit" and out.ok:
		await get_tree().process_frame
		get_tree().quit(int(args.get("code", 0)))


func _send(peer: StreamPeerTCP, msg: Dictionary) -> void:
	if peer.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		peer.put_data((JSON.stringify(msg) + "\n").to_utf8_buffer())


func _dispatch(cmd: String, a: Dictionary) -> Dictionary:
	match cmd:
		"ping":
			var scene := get_tree().current_scene
			return _ok({"godot": godot_version(), "scene": scene.scene_file_path if scene else "",
				"fps": Engine.get_frames_per_second()})
		"tree":
			var node := _node(a.get("path", "/root"))
			if node == null:
				return _err("no node at '%s'" % a.get("path", "/root"))
			return _ok(_tree(node, int(a.get("depth", 3))))
		"get":
			var node := _node(a.get("path"))
			if node == null:
				return _err("no node at '%s'" % a.get("path"))
			var prop := str(a.get("prop", ""))
			if not _has_prop(node, prop):
				return _err("%s has no property '%s'" % [node.get_path(), prop])
			return _ok(encode(node.get_indexed(NodePath(prop))))
		"set":
			var node := _node(a.get("path"))
			if node == null:
				return _err("no node at '%s'" % a.get("path"))
			var prop := str(a.get("prop", ""))
			if not _has_prop(node, prop):
				return _err("%s has no property '%s'" % [node.get_path(), prop])
			var np := NodePath(prop)
			var t := typeof(node.get_indexed(np))
			if t == TYPE_NIL:
				t = _declared_type(node.get_property_list(), prop)
			node.set_indexed(np, decode(a.get("value"), t))
			return _ok(encode(node.get_indexed(np)))
		"call":
			return await _call(a)
		"eval":
			var node := _node(a.get("path", "/root"))
			if node == null:
				return _err("no node at '%s'" % a.get("path", "/root"))
			var e := Expression.new()
			if e.parse(str(a.get("expr", ""))) != OK:
				return _err(e.get_error_text())
			var r = e.execute([], node, false)
			if e.has_execute_failed():
				return _err(e.get_error_text())
			return _ok(encode(r))
		"action":
			var action := StringName(str(a.get("action", "")))
			if not InputMap.has_action(action):
				return _err("unknown input action '%s'" % action)
			var ev := InputEventAction.new()
			ev.action = action
			ev.pressed = bool(a.get("pressed", true))
			ev.strength = float(a.get("strength", 1.0)) if ev.pressed else 0.0
			Input.parse_input_event(ev)
			Input.flush_buffered_events()
			return _ok({"action": String(action), "pressed": ev.pressed})
		"key":
			var kc = a.get("keycode")
			var code := 0
			if typeof(kc) == TYPE_STRING:
				code = OS.find_keycode_from_string(kc)
			elif typeof(kc) == TYPE_INT or typeof(kc) == TYPE_FLOAT:
				code = int(kc)
			if code == KEY_NONE:
				return _err("unknown keycode '%s'" % kc)
			var ev := InputEventKey.new()
			ev.keycode = code
			ev.physical_keycode = code
			ev.key_label = code
			ev.pressed = bool(a.get("pressed", true))
			if ev.pressed and code >= 32 and code < 127:
				ev.unicode = String.chr(code).to_lower().unicode_at(0)
			Input.parse_input_event(ev)
			Input.flush_buffered_events()
			return _ok({"keycode": OS.get_keycode_string(code), "pressed": ev.pressed})
		"frames":
			for i in maxi(int(a.get("n", 1)), 0):
				await get_tree().process_frame
			return _ok({"frame": Engine.get_process_frames()})
		"wait":
			var s := float(a.get("seconds", 0.0))
			await get_tree().create_timer(s, true, false, true).timeout
			return _ok({"seconds": s})
		"screenshot":
			var path := str(a.get("path", "")).replace("\\", "/")
			if not path.is_absolute_path() or path.begins_with("res://") or path.begins_with("user://"):
				return _err("screenshot path must be an absolute filesystem path")
			if DisplayServer.get_name() == "headless":
				return _err("screenshot unavailable: running headless (no rendering); launch windowed")
			await RenderingServer.frame_post_draw
			var img := get_viewport().get_texture().get_image()
			if img == null or img.is_empty():
				return _err("viewport texture is empty")
			var err := img.save_png(path)
			if err != OK:
				return _err("cannot save '%s': %s" % [path, error_string(err)])
			return _ok({"path": path, "size": [img.get_width(), img.get_height()]})
		"quit":
			return _ok({"code": int(a.get("code", 0))})
	return _err("unknown cmd '%s'" % cmd)


func _call(a: Dictionary) -> Dictionary:
	var node := _node(a.get("path"))
	if node == null:
		return _err("no node at '%s'" % a.get("path"))
	var method := str(a.get("method", ""))
	if not node.has_method(method):
		return _err("%s has no method '%s'" % [node.get_path(), method])
	var raw = a.get("args", [])
	var args: Array = raw if typeof(raw) == TYPE_ARRAY else [raw]
	for m in node.get_method_list():
		if m.name != method:
			continue
		var params: Array = m.args
		var vararg := (int(m.flags) & METHOD_FLAG_VARARG) != 0
		var required := params.size() - (m.default_args as Array).size()
		if args.size() < required or (args.size() > params.size() and not vararg):
			return _err("%s() takes %d..%d args, got %d" % [method, required, params.size(), args.size()])
		for i in mini(args.size(), params.size()):
			args[i] = decode(args[i], int(params[i].type))
		break
	var r = node.callv(method, args)
	if r is Object and is_instance_valid(r) and r.get_class() == "GDScriptFunctionState":
		r = await r.completed
	return _ok(encode(r))


func _node(path) -> Node:
	if path == null:
		return null
	return get_tree().root.get_node_or_null(NodePath(str(path)))


func _has_prop(node: Node, prop: String) -> bool:
	return prop != "" and (prop.get_slice(":", 0) in node)


func _tree(node: Node, depth: int) -> Dictionary:
	var d := {"name": String(node.name), "type": node.get_class(), "path": String(node.get_path())}
	var s: Script = node.get_script()
	if s:
		d["script"] = s.resource_path
	var kids := []
	if depth > 0:
		for ch in node.get_children():
			kids.append(_tree(ch, depth - 1))
	elif node.get_child_count() > 0:
		d["more"] = node.get_child_count()
	d["children"] = kids
	return d


## Port from user arg `--gd-bridge=<port>` / `--gd-bridge <port>`, else env GD_BRIDGE_PORT, else 0.
static func _requested_port() -> int:
	var args := OS.get_cmdline_user_args()
	for i in args.size():
		if args[i].begins_with("--gd-bridge="):
			return args[i].trim_prefix("--gd-bridge=").to_int()
		if args[i] == "--gd-bridge" and i + 1 < args.size():
			return args[i + 1].to_int()
	var env := OS.get_environment("GD_BRIDGE_PORT")
	return env.to_int() if env.is_valid_int() else 0


static func _ok(v) -> Dictionary:
	return {"ok": true, "result": v}


static func _err(msg: String) -> Dictionary:
	return {"ok": false, "error": msg}


static func _declared_type(props: Array, prop: String) -> int:
	if prop.contains(":"):
		return TYPE_NIL
	for p in props:
		if p.name == prop:
			return int(p.type)
	return TYPE_NIL


## "4.7.stable.official.5b4e0cb0f" (same form as `godot --version`).
static func godot_version() -> String:
	var v := Engine.get_version_info()
	var s := "%d.%d" % [v.major, v.minor]
	if v.patch > 0:
		s += ".%d" % v.patch
	return "%s.%s.%s.%s" % [s, v.status, v.build, str(v.hash).left(9)]


## Godot value -> JSON-safe value (contract: vectors/colors as arrays, other engine types via var_to_str).
static func encode(v):
	match typeof(v):
		TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_STRING:
			return v
		TYPE_FLOAT:
			return v if is_finite(v) else str(v)
		TYPE_STRING_NAME, TYPE_NODE_PATH:
			return str(v)
		TYPE_VECTOR2, TYPE_VECTOR2I:
			return [encode(v.x), encode(v.y)]
		TYPE_VECTOR3, TYPE_VECTOR3I:
			return [encode(v.x), encode(v.y), encode(v.z)]
		TYPE_COLOR:
			return [v.r, v.g, v.b, v.a]
		TYPE_OBJECT:
			if not is_instance_valid(v):
				return null
			var o := {"class": v.get_class()}
			if v is Node:
				o["path"] = String(v.get_path()) if v.is_inside_tree() else ""
			elif v is Resource:
				o["path"] = v.resource_path
			return o
		TYPE_DICTIONARY:
			var d := {}
			for k in v:
				d[k if typeof(k) == TYPE_STRING else str(k)] = encode(v[k])
			return d
		TYPE_ARRAY, TYPE_PACKED_BYTE_ARRAY, TYPE_PACKED_INT32_ARRAY, TYPE_PACKED_INT64_ARRAY, \
		TYPE_PACKED_FLOAT32_ARRAY, TYPE_PACKED_FLOAT64_ARRAY, TYPE_PACKED_STRING_ARRAY, \
		TYPE_PACKED_VECTOR2_ARRAY, TYPE_PACKED_VECTOR3_ARRAY, TYPE_PACKED_COLOR_ARRAY, \
		TYPE_PACKED_VECTOR4_ARRAY:
			var out := []
			for e in v:
				out.append(encode(e))
			return out
	return var_to_str(v)


## JSON value -> Godot value of variant type `t` where the shape allows it; otherwise unchanged.
static func decode(v, t: int):
	match typeof(v):
		TYPE_ARRAY:
			var a: Array = v
			match t:
				TYPE_VECTOR2:
					if a.size() == 2: return Vector2(a[0], a[1])
				TYPE_VECTOR2I:
					if a.size() == 2: return Vector2i(int(a[0]), int(a[1]))
				TYPE_VECTOR3:
					if a.size() == 3: return Vector3(a[0], a[1], a[2])
				TYPE_VECTOR3I:
					if a.size() == 3: return Vector3i(int(a[0]), int(a[1]), int(a[2]))
				TYPE_COLOR:
					if a.size() == 3: return Color(a[0], a[1], a[2])
					if a.size() == 4: return Color(a[0], a[1], a[2], a[3])
				TYPE_PACKED_BYTE_ARRAY, TYPE_PACKED_INT32_ARRAY, TYPE_PACKED_INT64_ARRAY, \
				TYPE_PACKED_FLOAT32_ARRAY, TYPE_PACKED_FLOAT64_ARRAY, TYPE_PACKED_STRING_ARRAY:
					return type_convert(a, t)
		TYPE_INT, TYPE_FLOAT:
			match t:
				TYPE_INT: return int(v)
				TYPE_FLOAT: return float(v)
				TYPE_BOOL: return bool(v)
		TYPE_STRING:
			match t:
				TYPE_STRING, TYPE_NIL:
					pass
				TYPE_STRING_NAME:
					return StringName(v)
				TYPE_NODE_PATH:
					return NodePath(v)
				TYPE_OBJECT:
					if (v as String).begins_with("res://") or (v as String).begins_with("uid://"):
						return ResourceLoader.load(v)
				_:
					var parsed = str_to_var(v)
					if typeof(parsed) == t:
						return parsed
	return v
