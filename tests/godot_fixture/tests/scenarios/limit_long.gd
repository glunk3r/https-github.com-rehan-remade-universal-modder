extends "res://addons/gd_remake/scenario.gd"
## Declares a 40 s case limit and returns after 31 s: past the runner's default 30 s, inside its own limit.


func time_limit_s() -> float:
	return 40.0


func run() -> void:
	await get_tree().create_timer(31.0).timeout
	expect(true, "ran past the default limit")
