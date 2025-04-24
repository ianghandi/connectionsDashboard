from flask import Flask, jsonify, request
from flask_cors import CORS
from services.pingfederate_api import get_saml_connections, get_oauth_clients
from utils.resolvers import resolve_connection_fields, resolve_oauth_client_fields

app = Flask(__name__)
CORS(app)

@app.route("/api/saml-connections", methods=["GET"])
def list_saml_connections():
    env = request.args.get("env", "dev")
    print(f"[DEBUG] Received request for SAML connections in env: {env}")
    try:
        raw = get_saml_connections(env, verify_ssl=False)
        result = [resolve_connection_fields(env, c, verify_ssl=False) for c in raw]
        print(f"[DEBUG] Returning {len(result)} SAML records")
        print(f"[DEBUG] First item: {result[0] if result else 'None'}")
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/oauth-connections", methods=["GET"])
def list_oauth_connections():
    env = request.args.get("env", "dev")
    print(f"[DEBUG] Received request for OAuth connections in env: {env}")
    try:
        raw = get_oauth_clients(env, verify_ssl=False)
        result = [resolve_oauth_client_fields(env, c, verify_ssl=False) for c in raw]
        print(f"[DEBUG] Returning {len(result)} OAuth records")
        print(f"[DEBUG] First item: {result[0] if result else 'None'}")
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
