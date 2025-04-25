import requests
from config import PINGFEDERATE_SERVERS
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Content-Type": "application/json",
    "X-XSRF-Header": "PingFederate"
}

cert_cache = {}
datastore_cache = {}
atm_cache = {}
oidc_cache = {}

def get_auth(env):
    config = PINGFEDERATE_SERVERS.get(env)
    if not config:
        raise ValueError(f"Unknown environment: {env}")
    return (config["username"], config["password"]), config["base_url"]

def preload_caches(env):
    auth, base_url = get_auth(env)

    def fetch_all(endpoint):
        url = f"{base_url}/pf-admin-api/v1/{endpoint}"
        try:
            res = requests.get(url, auth=auth, headers=headers, verify=False)
            return res.json().get("items", [])
        except Exception as e:
            print(f"[ERROR] Failed to preload {endpoint}: {e}")
            return []

    cert_cache[env] = {item.get("id"): item.get("name", item.get("id")) for item in fetch_all("keyPairs/signing") if item.get("id")}
    datastore_cache[env] = {item.get("id"): item.get("name", item.get("id")) for item in fetch_all("dataStores") if item.get("id")}
    atm_cache[env] = {item.get("id"): item.get("name", item.get("id")) for item in fetch_all("oauth/accessTokenManagers") if item.get("id")}
    oidc_cache[env] = {item.get("id"): item.get("name", item.get("id")) for item in fetch_all("oauth/openIdConnect/policies") if item.get("id")}

    print(f"[CACHE] Loaded certs: {len(cert_cache[env])}, datastores: {len(datastore_cache[env])}, ATMs: {len(atm_cache[env])}, OIDCs: {len(oidc_cache[env])}")

def get_cert_name_cached(env, id):
    return cert_cache.get(env, {}).get(id, id)

def get_datastore_name_cached(env, id):
    return datastore_cache.get(env, {}).get(id, id)

def get_access_token_manager_name_cached(env, id):
    return atm_cache.get(env, {}).get(id, id)

def get_oidc_policy_name_cached(env, id):
    return oidc_cache.get(env, {}).get(id, id)
