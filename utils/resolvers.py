import re
from utils.resolver_cache import (
    preload_caches,
    get_cert_name_cached,
    get_datastore_name_cached,
    get_access_token_manager_name_cached,
    get_oidc_policy_name_cached
)

def resolve_connection_fields(env, conn, verify_ssl=True):
    preload_caches(env)
    try:
        return {
            "appName": conn.get("name", "Unknown App"),
            "appID": conn.get("contactInfo", {}).get("phone", ""),
            "entityID": conn.get("entityId", ""),
            "active": "Yes" if conn.get("active") else "No",
            "idpURL": conn.get("ssoService", {}).get("ssoApplicationEndpoint", ""),
            "baseURL": conn.get("baseUrl", ""),
            "protocol": conn.get("protocol", ""),
            "enabledProfiles": conn.get("enabledProfiles", []),
            "incomingBindings": conn.get("incomingBindings", []),
            "dataStore": get_datastore_name_cached(env, conn.get("attributeMapping", {}).get("dataStoreRef", {}).get("id", "")),
            "issuanceCriteria": conn.get("issuanceCriteria", {}),
            "certificateName": get_cert_name_cached(env, conn.get("credentials", {}).get("signingSettings", {}).get("signingKeyPairRef", {}).get("id", ""))
        }
    except Exception as e:
        print(f"[ERROR] Exception inside resolve_connection_fields: {e}")
        return {
            "appName": "ERROR",
            "appID": "",
            "entityID": "",
            "active": "No",
            "idpURL": "",
            "baseURL": "",
            "protocol": "",
            "enabledProfiles": [],
            "incomingBindings": [],
            "dataStore": "",
            "issuanceCriteria": {},
            "certificateName": ""
        }


def extract_application_id(description):
    match = re.search(r'\bAD\d{8}\b', description or "")
    return match.group(0) if match else None

def resolve_oauth_client_fields(env, client, verify_ssl=False):
    preload_caches(env)
    return {
        "clientID": client.get("clientId", ""),
        "name": client.get("name", "Unknown Client"),
        "status": "ACTIVE" if client.get("enabled") else "INACTIVE",
        "grantTypes": client.get("grantTypes", []),
        "redirectURIs": client.get("redirectUris", []),
        "allowedScopes": client.get("allowedScopes", []),
        "accessTokenManager": get_access_token_manager_name_cached(env, client.get("accessTokenManagerRef", {}).get("id", "")),
        "oidcPolicy": get_oidc_policy_name_cached(env, client.get("openIdConnectPolicyRef", {}).get("id", "")),
        "applicationID": extract_application_id(client.get("description", ""))
    }
