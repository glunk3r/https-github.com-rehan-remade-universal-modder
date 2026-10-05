@tool
extends EditorPlugin
## Editor-only: enabling the plugin registers the GdBridge and Variants autoloads if missing.

const AUTOLOADS := {
	"GdBridge": "res://addons/gd_remake/bridge.gd",
	"Variants": "res://addons/gd_remake/variants.gd",
}


func _enable_plugin() -> void:
	for autoload_name in AUTOLOADS:
		if not ProjectSettings.has_setting("autoload/" + autoload_name):
			add_autoload_singleton(autoload_name, AUTOLOADS[autoload_name])


func _disable_plugin() -> void:
	for autoload_name in AUTOLOADS:
		if ProjectSettings.has_setting("autoload/" + autoload_name):
			remove_autoload_singleton(autoload_name)
