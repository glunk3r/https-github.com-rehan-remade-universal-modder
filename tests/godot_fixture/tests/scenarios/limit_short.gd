extends "res://addons/gd_remake/scenario.gd"
## Declares a 2 s case limit and never returns: the runner times it out after 2 s, not its --timeout.


func time_limit_s() -> float:
	return 2.0


func run() -> void:
	await get_tree().create_timer(3600.0).timeout
