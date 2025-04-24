
import requests
from config import PINGFEDERATE_SERVERS

headers = {"Content-Type": "application/json"}

def get_auth_headers(env):
    env_config = PINGFEDERATE_SERVERS.get(env)
    if not env_config:
        raise ValueError(f"Invalid environment: {env}")
    return (env_config["username"], env_config["password"]), env_config["base_url"]

def get_saml_connections(env):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/idp/sp-connections"
    return requests.get(url, auth=auth, headers=headers).json().get('items', [])

def get_oauth_clients(env):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/oauth/clients"
    return requests.get(url, auth=auth, headers=headers).json().get("items", [])

def get_datastore_name_by_id(env, id):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/dataStores/{id}"
    return requests.get(url, auth=auth, headers=headers).json().get("name", id)

def get_cert_name_by_id(env, id):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/keyPairs/signing/{id}"
    return requests.get(url, auth=auth, headers=headers).json().get("name", id)

def get_access_token_manager_name(env, id):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/oauth/accessTokenManagers/{id}"
    return requests.get(url, auth=auth, headers=headers).json().get("name", id)

def get_oidc_policy_name(env, id):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/oauth/openIdConnect/policies/{id}"
    return requests.get(url, auth=auth, headers=headers).json().get("name", id)
