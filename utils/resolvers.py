
import re
from services.pingfederate_api import (
    get_datastore_name_by_id,
    get_cert_name_by_id,
    get_access_token_manager_name,
    get_oidc_policy_name,
)

def resolve_connection_fields(env, conn):
    return {
        "appName": conn.get("name"),
        "appID": conn.get("phone"),
        "entityID": conn.get("entityId"),
        "active": conn.get("active"),
        "idpURL": conn.get("ssoService", {}).get("ssoApplicationEndpoint"),
        "baseURL": conn.get("baseUrl"),
        "protocol": conn.get("protocol"),
        "enabledProfiles": conn.get("enabledProfiles"),
        "incomingBindings": conn.get("incomingBindings"),
        "dataStore": get_datastore_name_by_id(env, conn.get("attributeMapping", {}).get("dataStoreRef", {}).get("id", "")),
        "issuanceCriteria": conn.get("issuanceCriteria"),
        "certificateName": get_cert_name_by_id(env, conn.get("credentials", {}).get("signingSettings", {}).get("signingKeyPairRef", {}).get("id", ""))
    }

def extract_application_id(description):
    match = re.search(r'\bAD\d{8}\b', description or "")
    return match.group(0) if match else None

def resolve_oauth_client_fields(env, client):
    return {
        "clientID": client.get("clientId"),
        "name": client.get("name"),
        "status": "ACTIVE" if client.get("enabled") else "INACTIVE",
        "grantTypes": client.get("grantTypes"),
        "redirectURIs": client.get("redirectUris"),
        "allowedScopes": client.get("allowedScopes"),
        "accessTokenManager": get_access_token_manager_name(env, client.get("accessTokenManagerRef", {}).get("id", "")),
        "oidcPolicy": get_oidc_policy_name(env, client.get("openIdConnectPolicyRef", {}).get("id", "")),
        "applicationID": extract_application_id(client.get("description"))
    }
