extends "res://addons/gd_remake/scenario.gd"
## The runner releases actions and frees the previous case's nodes between cases.


func cases() -> Array[Dictionary]:
	return [{"name": "hold"}, {"name": "check"}]


func run() -> void:
	if params.name == "hold":
		press("jump")
		var leftover := Node.new()
		leftover.name = "Leftover"
		get_tree().root.add_child(leftover)
		await frames(2)
		expect(Input.is_action_pressed("jump"), "jump held")
		return
	var t0 := Time.get_ticks_msec()
	await seconds(0.1)
	expect(Time.get_ticks_msec() - t0 >= 90, "seconds(0.1) waits ~100 ms")
	expect(not Input.is_action_pressed("jump"), "jump released by the runner between cases")
	expect(get_tree().root.get_node_or_null("Leftover") == null, "previous case's root nodes freed")
	expect_eq(get_tree().root.get_child_count(), 3, "root holds GdBridge, Variants and this scenario")
