extends "res://addons/gd_remake/scenario.gd"
## run() never returns within any sane timeout.


func run() -> void:
	await get_tree().create_timer(3600.0).timeout
