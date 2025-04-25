import re
from utils.resolver_cache import (
    preload_caches,
    get_cert_name_cached,
    get_access_token_manager_name_cached,
    get_oidc_policy_name_cached
)

def resolve_connection_fields(conn, certs_cache, datastores_cache):
    try:
        app_name = conn.get("name", "")
        app_id = conn.get("contactInfo", {}).get("phone", "")
        entity_id = conn.get("entityId", "")
        active = "Yes" if conn.get("active", False) else "No"

        sp_browser_sso = conn.get("spBrowserSso", {})
        idp_url = sp_browser_sso.get("ssoApplicationEndpoint", "")
        base_url = idp_url.split("/")[2] if idp_url else ""

        protocol = sp_browser_sso.get("protocol", "")
        enabled_profiles = sp_browser_sso.get("enabledProfiles", [])
        incoming_bindings = sp_browser_sso.get("incomingBindings", [])

        # Certificate name
        signing_ref_id = conn.get("credentials", {}).get("signingSettings", {}).get("signingKeyPairRef", {}).get("id", "")
        certificate_name = certs_cache.get(signing_ref_id, signing_ref_id) if signing_ref_id else ""

        # Data store ID from attributeSources
        data_store_id = ""
        mappings = sp_browser_sso.get("authenticationPolicyContractAssertionMappings", [])
        for mapping in mappings:
            sources = mapping.get("attributeSources", [])
            for src in sources:
                ref = src.get("dataStoreRef", {}).get("id")
                if ref:
                    data_store_id = ref
                    break
            if data_store_id:
                break

        data_store_name = datastores_cache.get(data_store_id, data_store_id) if data_store_id else ""

        # Issuance criteria expression
        issuance_expression = ""
        for mapping in conn.get("authenticationPolicyContractAssertionMappings", []):
            expression_criteria = mapping.get("issuanceCriteria", {}).get("expressionCriteria", [])
            if isinstance(expression_criteria, list) and expression_criteria:
                issuance_expression = expression_criteria[0].get("expression", "")
                break

        # SSO Service Endpoint URL
        sso_service_url = ""
        try:
            endpoints = sp_browser_sso.get("ssoServiceEndpoints", [])
            if endpoints:
                sso_service_url = endpoints[0].get("url", "")
        except Exception as e:
            print(f"[ERROR] Failed to extract SSO Service URL: {e}")

        return {
            "appName": app_name,
            "appID": app_id,
            "entityID": entity_id,
            "active": active,
            "idpURL": idp_url,
            "baseURL": base_url,
            "protocol": protocol,
            "enabledProfiles": enabled_profiles,
            "incomingBindings": incoming_bindings,
            "dataStore": data_store_name,
            "issuanceCriteria": issuance_expression,
            "certificateName": certificate_name,
            "ssoServiceEndpointURL": sso_service_url
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
            "certificateName": "",
            "ssoServiceEndpointURL": ""
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
