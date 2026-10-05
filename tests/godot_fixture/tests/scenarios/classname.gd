extends GdScenario
## class_name form: only loads once the global class cache exists (godot --import / editor).


func run() -> void:
	await frames(1)
	expect(true, "ok")
