import requests
import urllib3
from config import PINGFEDERATE_SERVERS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {"Content-Type": "application/json"}

def get_auth_headers(env):
    env_config = PINGFEDERATE_SERVERS.get(env)
    if not env_config:
        raise ValueError(f"Invalid environment: {env}")
    return (env_config["username"], env_config["password"]), env_config["base_url"]

def get_saml_connections(env, verify_ssl=True):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/idp/spConnections"
    print(f"[DEBUG] Fetching SAML connections from: {url}")
    response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl)
    print(f"[DEBUG] Response status: {response.status_code}")
    try:
        json_data = response.json()
        print(f"[DEBUG] Response JSON (truncated): {str(json_data)[:300]}")
    except Exception as e:
        print(f"[ERROR] Failed to parse SAML response JSON: {e}")
        return []
    return json_data.get("items", [])

def get_oauth_clients(env, verify_ssl=True):
    auth, base_url = get_auth_headers(env)
    url = f"{base_url}/pf-admin-api/v1/oauth/clients"
    print(f"[DEBUG] Fetching OAuth clients from: {url}")
    response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl)
    print(f"[DEBUG] Response status: {response.status_code}")
    try:
        json_data = response.json()
        print(f"[DEBUG] Response JSON (truncated): {str(json_data)[:300]}")
    except Exception as e:
        print(f"[ERROR] Failed to parse OAuth response JSON: {e}")
        return []
    return json_data.get("items", [])

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
