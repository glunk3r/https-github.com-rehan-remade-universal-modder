extends "res://addons/gd_remake/scenario.gd"
## Runtime script error after an await (must become status "error", not pass/timeout).


func run() -> void:
	await frames(2)
	var n: Node = null
	n.queue_free()
	await frames(600)
