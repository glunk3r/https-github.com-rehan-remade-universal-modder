extends "res://addons/gd_remake/scenario.gd"
## Variants autoload: active choice, load() fallback to res://assets, bind() + set_active().
## Expected hero variant comes from user arg --expect-hero=<name> (default "a").

const Net := preload("res://addons/gd_remake/net.gd")


func run() -> void:
	var want := Net.url_param("expect-hero", "a")
	expect_eq(Variants.active("hero"), want, "active hero variant")
	var hero := Variants.load("hero")
	expect(hero is Texture2D, "hero loads as Texture2D")
	expect_eq(hero.resource_path if hero else "", "res://variants/hero/%s.png" % want, "hero path")
	var enemy := Variants.load("enemy")
	expect_eq(enemy.resource_path if enemy else "", "res://assets/enemy.png", "enemy falls back to promoted file")
	var sprite := Sprite2D.new()
	add_child(sprite)
	Variants.bind(sprite, "texture", "hero")
	var other := "a" if want == "b" else "b"
	Variants.set_active("hero", other)
	expect_eq(sprite.texture.resource_path if sprite.texture else "", "res://variants/hero/%s.png" % other, "bind follows set_active")
	Variants.set_active("hero", want)
	metric("slots", Variants.slots())
	metric("hero", hero.resource_path if hero else "")
	metric("enemy", enemy.resource_path if enemy else "")
