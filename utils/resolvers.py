import re
from utils.resolver_cache import (
    preload_caches,
    get_cert_name_cached,
    get_access_token_manager_name_cached,
    get_oidc_policy_name_cached
)

def resolve_connection_fields(env, conn, verify_ssl=True):
    preload_caches(env)

    try:
        # Flatten all attributeSources across all mappings
        all_sources = [
            src for mapping in conn.get("authenticationPolicyContractAssertionMappings", [])
            for src in mapping.get("attributeSources", [])
        ]
        ds_id = next((
            src.get("dataStoreRef", {}).get("id")
            for src in all_sources
            if src.get("dataStoreRef", {}).get("id")
        ), "")
        print(f"[DEBUG] Resolved datastore ID: {ds_id or '[None]'}")

        # 🛠 Correct extraction of issuanceCriteria.expressionCriteria.expression
        issuance_expression = ""
        try:
            expr_criteria = conn.get("issuanceCriteria", {}).get("expressionCriteria", [])
            if isinstance(expr_criteria, list) and expr_criteria:
                issuance_expression = expr_criteria[0].get("expression", "")
        except Exception as e:
            print(f"[ERROR] Failed to extract issuance expression: {e}")

        return {
            "appName": conn.get("name", "Unknown App"),
            "appID": conn.get("contactInfo", {}).get("phone", ""),
            "entityID": conn.get("entityId", ""),
            "active": "Yes" if conn.get("active") else "No",
            "idpURL": conn.get("spBrowserSso", {}).get("ssoApplicationEndpoint", ""),
            "baseURL": conn.get("baseUrl", ""),
            "protocol": conn.get("spBrowserSso", {}).get("protocol", ""),
            "enabledProfiles": conn.get("spBrowserSso", {}).get("enabledProfiles", []),
            "incomingBindings": conn.get("spBrowserSso", {}).get("incomingBindings", []),
            "dataStore": ds_id,
            "issuanceCriteria": issuance_expression,
            "certificateName": get_cert_name_cached(
                env,
                conn.get("credentials", {}).get("signingSettings", {}).get("signingKeyPairRef", {}).get("id", "")
            )
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
            "issuanceCriteria": "",
            "certificateName": ""
        }

def resolve_oauth_client_fields(env, client, verify_ssl=True):
    preload_caches(env)

    desc = client.get("description", "")
    match = re.search(r"(AD\d+)", desc)
    app_id = match.group(1) if match else ""

    return {
        "clientID": client.get("clientId", ""),
        "appName": client.get("name", "Unknown App"),
        "appID": app_id,
        "status": client.get("enabled", False),
        "grantTypes": client.get("grantTypes", []),
        "redirectURIs": client.get("redirectUris", []),
        "allowedScopes": client.get("restrictedScopes", []),
        "accessTokenManager": get_access_token_manager_name_cached(
            env,
            client.get("accessTokenManagerRef", {}).get("id", "")
        ),
        "oidcPolicy": get_oidc_policy_name_cached(
            env,
            client.get("policyRef", {}).get("id", "")
        )
    }
