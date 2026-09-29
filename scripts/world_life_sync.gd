extends Node

signal sync_finished(ok: bool, count: int)

const GATEWAY_BASE := "https://world-life-api.bomsronthai.workers.dev"
const MANIFEST_URL := GATEWAY_BASE + "/resource"
const CACHE_DIR := "user://world_life_resources"
const CACHE_MANIFEST := "user://world_life_manifest.json"
const MANIFEST_TIMEOUT := 8.0
const DOWNLOAD_TIMEOUT := 0.0

var _manifest_request: HTTPRequest
var _download_requests: Array[HTTPRequest] = []

func _ready() -> void:
	_sync_manifest()

func _sync_manifest() -> void:
	_manifest_request = HTTPRequest.new()
	_manifest_request.timeout = MANIFEST_TIMEOUT
	_manifest_request.body_size_limit = 2 * 1024 * 1024
	add_child(_manifest_request)
	_manifest_request.request_completed.connect(_on_manifest_completed)
	var err := _manifest_request.request(MANIFEST_URL)
	if err != OK:
		push_warning("World Life Gateway request could not start: %s" % err)
		sync_finished.emit(false, 0)

func _on_manifest_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS or response_code < 200 or response_code >= 300:
		push_warning("World Life Gateway unavailable; continuing offline.")
		sync_finished.emit(false, 0)
		return

	var text := body.get_string_from_utf8()
	var parsed = JSON.parse_string(text)
	var resources := _extract_resources(parsed)
	if resources.is_empty():
		push_warning("World Life Gateway returned no usable resource manifest.")
		sync_finished.emit(false, 0)
		return

	DirAccess.make_dir_recursive_absolute(CACHE_DIR)
	var cache := FileAccess.open(CACHE_MANIFEST, FileAccess.WRITE)
	if cache:
		cache.store_string(JSON.stringify(parsed))
		cache.close()

	var downloaded := 0
	for item in resources:
		if item is Dictionary and item.has("url") and str(item.url).begins_with("https://"):
			var name := _safe_name(str(item.get("name", item.get("path", ""))))
			if name != "":
				_download_resource(str(item.url), name)
				downloaded += 1

	push_warning("World Life Gateway connected. Manifest entries: %d" % resources.size())
	sync_finished.emit(true, resources.size())

func _extract_resources(parsed) -> Array:
	if parsed is Array:
		return parsed
	if parsed is Dictionary:
		for key in ["resources", "files", "items", "data"]:
			if parsed.get(key) is Array:
				return parsed[key]
		if parsed.has("name") or parsed.has("path"):
			return [parsed]
	return []

func _safe_name(value: String) -> String:
	var name := value.get_file()
	if name.is_empty() or name.contains("..") or not name.ends_with(".smf"):
		return ""
	return name

func _download_resource(url: String, name: String) -> void:
	var target := CACHE_DIR.path_join(name)
	if FileAccess.file_exists(target):
		return
	var req := HTTPRequest.new()
	req.timeout = DOWNLOAD_TIMEOUT
	req.download_file = target + ".part"
	req.keep_partial_download = false
	add_child(req)
	_download_requests.append(req)
	req.request_completed.connect(_on_resource_completed.bind(req, target))
	var err := req.request(url)
	if err != OK:
		req.queue_free()

func _on_resource_completed(result: int, response_code: int, _headers: PackedStringArray, _body: PackedByteArray, req: HTTPRequest, target: String) -> void:
	var partial := target + ".part"
	if result == HTTPRequest.RESULT_SUCCESS and response_code >= 200 and response_code < 300 and FileAccess.file_exists(partial):
		DirAccess.rename_absolute(partial, target)
	elif FileAccess.file_exists(partial):
		DirAccess.remove_absolute(partial)
	_download_requests.erase(req)
	req.queue_free()
