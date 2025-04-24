import requests
import urllib3
from config import PINGFEDERATE_SERVERS

# Suppress SSL warnings in development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {"Content-Type": "application/json"}

def get_auth_headers(env):
    env_config = PINGFEDERATE_SERVERS.get(env)
    if not env_config:
        raise ValueError(f"Invalid environment: {env}")
    return (env_config["username"], env_config["password"]), env_config["base_url"]

def get_saml_connections(env, verify_ssl=True):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/idp/sp-connections"
    return requests.get(url, auth=auth, headers=headers, verify=verify_ssl).json().get('items', [])

def get_oauth_clients(env, verify_ssl=True):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/oauth/clients"
    return requests.get(url, auth=auth, headers=headers, verify=verify_ssl).json().get("items", [])

def get_datastore_name_by_id(env, id, verify_ssl=True):
    if not id:
        return ""
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/dataStores/{id}"
    response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl)
    return response.json().get("name", id) if response.ok else id

def get_cert_name_by_id(env, id, verify_ssl=True):
    if not id:
        return ""
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/keyPairs/signing/{id}"
    response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl)
    return response.json().get("name", id) if response.ok else id

def get_access_token_manager_name(env, id, verify_ssl=True):
    if not id:
        return ""
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/oauth/accessTokenManagers/{id}"
    response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl)
    return response.json().get("name", id) if response.ok else id

def get_oidc_policy_name(env, id, verify_ssl=True):
    if not id:
        return ""
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/oauth/openIdConnect/policies/{id}"
    response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl)
    return response.json().get("name", id) if response.ok else id
