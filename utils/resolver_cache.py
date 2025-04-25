import requests
import re
from config import PING_ENVIRONMENTS

# Caching layer
_CACHE = {}

def _get_env_config(env):
    env_conf = PING_ENVIRONMENTS[env]
    base_url = env_conf["base_url"]
    headers = {
        "Authorization": f"Basic {env_conf['auth']}",
        "X-XSRF-Header": "PingFederate"
    }
    verify_ssl = env_conf.get("verify_ssl", True)
    return base_url, headers, verify_ssl

def preload_caches(env):
    base_url, headers, verify_ssl = _get_env_config(env)

    # Load Certificates
    if f"{env}_certs" not in _CACHE:
        try:
            print(f"[DEBUG] Loading certs for {env}")
            url = f"{base_url}/pf-admin-api/v1/keyPairs/signing"
            resp = requests.get(url, headers=headers, verify=verify_ssl)
            resp.raise_for_status()
            items = resp.json().get("items", [])
            _CACHE[f"{env}_certs"] = {item["id"]: item.get("name", item["id"]) for item in items}
        except Exception as e:
            print(f"[ERROR] Failed to load certs for {env}: {e}")
            _CACHE[f"{env}_certs"] = {}

    # Load Access Token Managers
    if f"{env}_atms" not in _CACHE:
        try:
            print(f"[DEBUG] Loading Access Token Managers for {env}")
            url = f"{base_url}/pf-admin-api/v1/accessTokenManagers"
            resp = requests.get(url, headers=headers, verify=verify_ssl)
            resp.raise_for_status()
            items = resp.json().get("items", [])
            _CACHE[f"{env}_atms"] = {item["id"]: item.get("name", item["id"]) for item in items}
        except Exception as e:
            print(f"[ERROR] Failed to load ATMs for {env}: {e}")
            _CACHE[f"{env}_atms"] = {}

    # Load OIDC Policies
    if f"{env}_oidc_policies" not in _CACHE:
        try:
            print(f"[DEBUG] Loading OIDC Policies for {env}")
            url = f"{base_url}/pf-admin-api/v1/oidcPolicies"
            resp = requests.get(url, headers=headers, verify=verify_ssl)
            resp.raise_for_status()
            items = resp.json().get("items", [])
            _CACHE[f"{env}_oidc_policies"] = {item["id"]: item.get("name", item["id"]) for item in items}
        except Exception as e:
            print(f"[ERROR] Failed to load OIDC Policies for {env}: {e}")
            _CACHE[f"{env}_oidc_policies"] = {}

    # Load Datastores
    if f"{env}_datastores" not in _CACHE:
        try:
            print(f"[DEBUG] Loading Datastores for {env}")
            url = f"{base_url}/pf-admin-api/v1/dataStores"
            resp = requests.get(url, headers=headers, verify=verify_ssl)
            resp.raise_for_status()
            items = resp.json().get("items", [])
            _CACHE[f"{env}_datastores"] = {item["id"]: item.get("name", item["id"]) for item in items}
        except Exception as e:
            print(f"[ERROR] Failed to load Datastores for {env}: {e}")
            _CACHE[f"{env}_datastores"] = {}

# --------------------
# Getter helper functions
# --------------------

def get_cert_name_cached(env, cert_id):
    preload_caches(env)
    return _CACHE.get(f"{env}_certs", {}).get(cert_id, cert_id)

def get_access_token_manager_name_cached(env, atm_id):
    preload_caches(env)
    return _CACHE.get(f"{env}_atms", {}).get(atm_id, atm_id)

def get_oidc_policy_name_cached(env, policy_id):
    preload_caches(env)
    return _CACHE.get(f"{env}_oidc_policies", {}).get(policy_id, policy_id)

def get_datastore_name_cached(env, datastore_id):
    preload_caches(env)
    return _CACHE.get(f"{env}_datastores", {}).get(datastore_id, datastore_id)
