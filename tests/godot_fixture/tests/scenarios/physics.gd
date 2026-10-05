extends "res://addons/gd_remake/scenario.gd"
## Passing scenario, two cases: free fall speed and jump apex (press/frames/expect_near/metric).


func cases() -> Array[Dictionary]:
	return [{"name": "fall", "frames": 30}, {"name": "jump"}]


func run() -> void:
	if params.name == "fall":
		var p := spawn("res://player.tscn") as CharacterBody2D
		p.position = Vector2(240, 0)
		await frames(params.frames)
		expect_near(p.velocity.y, 980.0 * params.frames / 60.0, 0.5, "free-fall speed")
		metric("fall_speed", p.velocity.y)
		metric("fall_pos", p.position)
		return
	var main := spawn("res://main.tscn")
	var p: CharacterBody2D = main.get_node("Player")
	var counter := main.get_node("Counter")
	await frames(45)
	expect(p.is_on_floor(), "player rests on the floor")
	var floor_y := p.position.y
	press("jump")
	await frames(2)
	release("jump")
	var apex := floor_y
	for i in 60:
		await frames(1)
		apex = minf(apex, p.position.y)
	expect_eq(p.jumps, 1, "one jump")
	expect_eq(counter.jump_events, 1, "_unhandled_input saw the press")
	expect_near(floor_y - apex, 81.6, 6.0, "apex height px")
	metric("apex_px", floor_y - apex)
	metric("physics_frames", counter.physics_frames)
