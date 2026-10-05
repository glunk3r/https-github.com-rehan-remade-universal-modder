extends "res://addons/gd_remake/scenario.gd"
## Grid demo (`--grid`): three cases differing only by params, one fails on purpose.
## Grid cases run concurrently and share the global Input singleton, so they must not press().


func cases() -> Array[Dictionary]:
	return [
		{"name": "left", "x": 80.0},
		{"name": "center", "x": 240.0},
		{"name": "off_floor", "x": 600.0},
	]


func run() -> void:
	var main := spawn("res://main.tscn")
	var p: CharacterBody2D = main.get_node("Player")
	p.position.x = params.x
	await frames(60)
	expect(p.is_on_floor(), "player lands on the floor")
	metric("pos", p.position)
