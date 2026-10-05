class_name GdNet
extends RefCounted
## Multiplayer transport helpers shared by desktop and web builds (static functions).
##
## Without the class cache use `const GdNet = preload("res://addons/gd_remake/net.gd")`.
##   multiplayer.multiplayer_peer = GdNet.server(9080)                      # desktop host
##   multiplayer.multiplayer_peer = GdNet.client("127.0.0.1", 9080)         # desktop or web client
##   var room := GdNet.url_param("room", "lobby")   # web: ?room=x, desktop: -- --room=x


## WebSocket multiplayer server listening on all interfaces (desktop/server builds; browsers
## cannot host). Returns null and pushes an error when the port cannot be opened.
static func server(port: int) -> MultiplayerPeer:
	var peer := WebSocketMultiplayerPeer.new()
	var err := peer.create_server(port)
	if err != OK:
		push_error("GdNet.server(%d): %s" % [port, error_string(err)])
		return null
	return peer


## WebSocket multiplayer client to ws://host:port. Connection completes asynchronously
## (multiplayer.connected_to_server / connection_failed).
static func client(host: String, port: int) -> MultiplayerPeer:
	var peer := WebSocketMultiplayerPeer.new()
	var url := "ws://%s:%d" % [host, port]
	var err := peer.create_client(url)
	if err != OK:
		push_error("GdNet.client(%s): %s" % [url, error_string(err)])
		return null
	return peer


## Web: query parameter `name` of the page URL (?name=v). Elsewhere: user arg `--name=v`
## (or `--name v`). Returns `default_value` when absent.
static func url_param(name: String, default_value := "") -> String:
	if OS.has_feature("web"):
		var search = JavaScriptBridge.eval("window.location.search", true)
		if typeof(search) == TYPE_STRING:
			for pair in (search as String).trim_prefix("?").split("&", false):
				var key := pair.get_slice("=", 0).uri_decode()
				if key == name:
					return pair.substr(key.length() + 1).uri_decode() if pair.contains("=") else ""
	var args := OS.get_cmdline_user_args()
	for i in args.size():
		if args[i].begins_with("--%s=" % name):
			return args[i].substr(name.length() + 3)
		if args[i] == "--" + name and i + 1 < args.size():
			return args[i + 1]
	return default_value
