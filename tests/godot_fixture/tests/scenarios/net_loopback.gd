extends "res://addons/gd_remake/scenario.gd"
## GdNet server + client in one process connect over ws://127.0.0.1.

const Net := preload("res://addons/gd_remake/net.gd")


func run() -> void:
	var port := 47900 + randi() % 90
	var server := Net.server(port)
	var client := Net.client("127.0.0.1", port)
	expect(server != null and client != null, "peers created")
	if server == null or client == null:
		return
	var waited := 0
	while waited < 300 and client.get_connection_status() != MultiplayerPeer.CONNECTION_CONNECTED:
		server.poll()
		client.poll()
		await frames(1)
		waited += 1
	expect_eq(client.get_connection_status(), MultiplayerPeer.CONNECTION_CONNECTED, "client connected")
	expect(client.get_unique_id() > 1, "client got a peer id")
	metric("connect_frames", waited)
	expect_eq(Net.url_param("room", "lobby"), "lobby", "url_param default")
	client.close()
	server.close()
