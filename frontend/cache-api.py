from flask import Flask, request, jsonify
import redis
import requests
import os
import yaml
import json

# Load config from environment or file
# Default to local 'config-api.yaml' if CONFIG_PATH not provided (works on dev machine)
config_path = os.getenv("CONFIG_PATH", os.path.join(os.path.dirname(__file__), "config-api.yaml"))
config = {}
try:
	with open(config_path, "r", encoding="utf-8") as f:
		config = yaml.safe_load(f) or {}
except FileNotFoundError:
	config = {}
except Exception:
	# If YAML is malformed, fall back to empty config but continue running
	config = {}

# Read settings: environment variables have priority over config file
def _get_int_env(name, default):
	val = os.getenv(name)
	if val is not None:
		try:
			return int(val)
		except ValueError:
			pass
	# try to read from config
	parts = name.split("_")
	# fallback to provided default
	return default

REDIS_HOST = os.getenv("REDIS_HOST", config.get("redis", {}).get("host", "redis"))
REDIS_PORT = _get_int_env("REDIS_PORT", config.get("redis", {}).get("port", 6379))

BACKEND_HOST = os.getenv("BACKEND_HOST", config.get("backend", {}).get("host", "backend-api"))
BACKEND_PORT = _get_int_env("BACKEND_PORT", config.get("backend", {}).get("port", 8080))

APP_PORT = _get_int_env("APP_PORT", config.get("app", {}).get("port", 5000))

app = Flask(__name__)

# Create Redis client with a small timeout to avoid long blocking on startup
try:
	r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
	# Optional: ping to validate connection (don't fail startup on connection issues)
	try:
		r.ping()
	except Exception:
		# We'll handle redis errors at runtime
		pass
except Exception:
	r = None


@app.route("/user")
def get_user():
	user_id = request.args.get("id")
	if not user_id:
		return jsonify({"error": "missing id parameter"}), 400

	# Try cache first
	if r is not None:
		try:
			cached = r.get(user_id)
		except Exception:
			cached = None
	else:
		cached = None

	if cached:
		try:
			user_obj = json.loads(cached)
		except Exception:
			# If stored value is not valid JSON, return raw string
			user_obj = cached
		return jsonify({"cached": True, "user": user_obj})

	# Fetch from backend
	try:
		resp = requests.get(f"http://{BACKEND_HOST}:{BACKEND_PORT}/user", params={"id": user_id}, timeout=5)
	except requests.RequestException as e:
		return jsonify({"error": "failed to reach backend", "details": str(e)}), 502

	if resp.status_code == 200:
		# Store JSON text in cache if possible
		try:
			text = resp.text
			if r is not None:
				try:
					r.set(user_id, text, ex=60)
				except Exception:
					pass
			return jsonify({"cached": False, "user": resp.json()})
		except ValueError:
			# Backend returned non-json body
			return resp.text, 200

	return resp.text, resp.status_code


if __name__ == "__main__":
	# Allow binding port from environment
	app.run(host="0.0.0.0", port=APP_PORT)
