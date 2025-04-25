import re
from utils.resolver_cache import (
    preload_caches,
    get_cert_name_cached,
    get_access_token_manager_name_cached,
    get_oidc_policy_name_cached,
    get_datastore_name_cached
)

def resolve_saml_connection_fields(env, conn):
    try:
        preload_caches(env)

        name = conn.get("name", "")
        entity_id = conn.get("entityId", "")
        active = "Yes" if conn.get("active", False) else "No"
        app_id = conn.get("contactInfo", {}).get("phone", "")

        sp_sso = conn.get("spBrowserSso", {})
        protocol = sp_sso.get("protocol", "")
        enabled_profiles = sp_sso.get("enabledProfiles", [])
        incoming_bindings = sp_sso.get("incomingBindings", [])
        idp_url = sp_sso.get("ssoApplicationEndpoint", "")
        sso_endpoints = sp_sso.get("ssoServiceEndpoints", [])
        base_url = sso_endpoints[0].get("url", "") if sso_endpoints else ""

        issuance_criteria = ""
        mappings = conn.get("spBrowserSso", {}).get("authenticationPolicyContractAssertionMappings", [])
        if mappings:
            criteria = mappings[0].get("issuanceCriteria", {})
            expression_criteria = criteria.get("expressionCriteria", [])
            if expression_criteria:
                issuance_criteria = expression_criteria[0].get("expression", "")
            elif criteria.get("conditionalCriteria"):
                issuance_criteria = str(criteria["conditionalCriteria"])

        datastore_id = ""
        if mappings:
            sources = mappings[0].get("attributeSources", [])
            if sources:
                ds_ref = sources[0].get("dataStoreRef", {}).get("id", "")
                if ds_ref:
                    datastore_id = get_datastore_name_cached(env, ds_ref)

        cert_id = conn.get("credentials", {}).get("signingSettings", {}).get("signingKeyPairRef", {}).get("id", "")
        cert_name = get_cert_name_cached(env, cert_id)

        return {
            "appName": name,
            "appID": app_id,
            "entityID": entity_id,
            "active": active,
            "idpURL": idp_url,
            "baseURL": base_url,
            "protocol": protocol,
            "enabledProfiles": enabled_profiles,
            "incomingBindings": incoming_bindings,
            "dataStore": datastore_id,
            "issuanceCriteria": issuance_criteria,
            "certificateName": cert_name
        }

    except Exception as e:
        print(f"[ERROR] Exception inside resolve_saml_connection_fields: {e}")
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
