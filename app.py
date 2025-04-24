
from flask import Flask, jsonify, request
from services.pingfederate_api import get_saml_connections, get_oauth_clients
from utils.resolvers import resolve_connection_fields, resolve_oauth_client_fields

app = Flask(__name__)

@app.route("/api/saml-connections", methods=["GET"])
def list_saml_connections():
    env = request.args.get("env", "dev")
    try:
        raw = get_saml_connections(env)
        return jsonify([resolve_connection_fields(env, c) for c in raw])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/oauth-connections", methods=["GET"])
def list_oauth_connections():
    env = request.args.get("env", "dev")
    try:
        raw = get_oauth_clients(env)
        return jsonify([resolve_oauth_client_fields(env, c) for c in raw])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
