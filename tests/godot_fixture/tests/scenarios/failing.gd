extends "res://addons/gd_remake/scenario.gd"
## Always fails: two recorded failures.


func run() -> void:
	await frames(3)
	expect_eq(1 + 1, 3, "arithmetic")
	expect(false, "second failure")
