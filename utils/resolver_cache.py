import requests
import re
from config import PINGFEDERATE_ENVIRONMENTS

cert_cache = {}
datastore_cache = {}
atm_cache = {}
oidc_cache = {}
preloaded_envs = set()

def _get_env_config(env):
    env_conf = PINGFEDERATE_ENVIRONMENTS[env]
    base_url = env_conf["base_url"]
    headers = {
        "Authorization": f"Basic {env_conf['auth']}",
        "X-XSRF-Header": "PingFederate"
    }
    verify_ssl = env_conf.get("verify_ssl", True)
    return base_url, headers, verify_ssl

def preload_caches(env):
    if env in preloaded_envs:
        return

    base_url, headers, verify_ssl = _get_env_config(env)

    try:
        # Certs
        cert_url = f"{base_url}/pf-admin-api/v1/keyPairs/signing"
        cert_resp = requests.get(cert_url, headers=headers, verify=verify_ssl)
        cert_resp.raise_for_status()
        certs = cert_resp.json().get("items", [])
        for cert in certs:
            cert_cache[(env, cert["id"])] = cert.get("name", cert["id"])

        # Datastores
        ds_url = f"{base_url}/pf-admin-api/v1/dataStores"
        ds_resp = requests.get(ds_url, headers=headers, verify=verify_ssl)
        ds_resp.raise_for_status()
        datastores = ds_resp.json().get("items", [])
        for ds in datastores:
            datastore_cache[(env, ds["id"])] = ds.get("name", ds["id"])

        # Access Token Managers
        atm_url = f"{base_url}/pf-admin-api/v1/accessTokenManagers"
        atm_resp = requests.get(atm_url, headers=headers, verify=verify_ssl)
        atm_resp.raise_for_status()
        atms = atm_resp.json().get("items", [])
        for atm in atms:
            atm_cache[(env, atm["id"])] = atm.get("name", atm["id"])

        # OIDC Policies
        oidc_url = f"{base_url}/pf-admin-api/v1/oidcPolicies"
        oidc_resp = requests.get(oidc_url, headers=headers, verify=verify_ssl)
        oidc_resp.raise_for_status()
        oidc_policies = oidc_resp.json().get("items", [])
        for oidc in oidc_policies:
            oidc_cache[(env, oidc["id"])] = oidc.get("name", oidc["id"])

        preloaded_envs.add(env)
        print(f"[DEBUG] Successfully preloaded caches for environment: {env}")

    except Exception as e:
        print(f"[ERROR] Failed to preload caches for {env}: {e}")

def get_cert_name_cached(env, cert_id):
    preload_caches(env)
    return cert_cache.get((env, cert_id), cert_id)

def get_access_token_manager_name_cached(env, atm_id):
    preload_caches(env)
    return atm_cache.get((env, atm_id), atm_id)

def get_oidc_policy_name_cached(env, policy_id):
    preload_caches(env)
    return oidc_cache.get((env, policy_id), policy_id)

def get_datastore_name_cached(env, datastore_id):
    preload_caches(env)
    return datastore_cache.get((env, datastore_id), datastore_id)
