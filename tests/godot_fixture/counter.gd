extends Node

var physics_frames := 0
var jump_events := 0


func _physics_process(_delta: float) -> void:
	physics_frames += 1


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("jump"):
		jump_events += 1
