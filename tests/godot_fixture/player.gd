extends CharacterBody2D

const GRAVITY := 980.0
const JUMP_VELOCITY := -400.0

var jumps := 0


func _physics_process(delta: float) -> void:
	velocity.y += GRAVITY * delta
	if is_on_floor() and Input.is_action_just_pressed("jump"):
		velocity.y = JUMP_VELOCITY
		jumps += 1
	move_and_slide()
