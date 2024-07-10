import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
from datetime import datetime, timedelta

# Deaktivieren von SSL-Warnungen (nur für Testzwecke)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API-Konfiguration
ISE_HOST = "https://ise.beispiel.com"
USERNAME = "api_user"
PASSWORD = "api_password"
BASE_URL = f"{ISE_HOST}/ers/config"

# Authentifizierung und Header
auth = HTTPBasicAuth(USERNAME, PASSWORD)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_identity_groups():
    """Abrufen aller Identity Groups"""
    url = f"{BASE_URL}/identitygroup"
    response = requests.get(url, auth=auth, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()['SearchResult']['resources']
    else:
        print(f"Fehler beim Abrufen der Identity Groups: {response.status_code}")
        return None

def get_endpoints_in_group(group_id):
    """Abrufen aller Endpunkte in einer bestimmten Identity Group"""
    url = f"{BASE_URL}/endpoint?filter=identityGroup.id.EQ.{group_id}"
    response = requests.get(url, auth=auth, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()['SearchResult']['resources']
    else:
        print(f"Fehler beim Abrufen der Endpunkte für Gruppe {group_id}: {response.status_code}")
        return None

def delete_endpoint(endpoint_id):
    """Löschen eines Endpunkts"""
    url = f"{BASE_URL}/endpoint/{endpoint_id}"
    response = requests.delete(url, auth=auth, headers=headers, verify=False)
    if response.status_code == 204:
        print(f"Endpunkt {endpoint_id} erfolgreich gelöscht")
    else:
        print(f"Fehler beim Löschen des Endpunkts {endpoint_id}: {response.status_code}")

def is_inactive(last_seen):
    """Überprüfen, ob ein Endpunkt seit mehr als 60 Tagen inaktiv ist"""
    if not last_seen:
        return True
    last_seen_date = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%S.%fZ")
    return (datetime.now() - last_seen_date) > timedelta(days=60)

def main():
    groups = get_identity_groups()
    if not groups:
        return

    for group in groups:
        print(f"Verarbeite Gruppe: {group['name']}")
        endpoints = get_endpoints_in_group(group['id'])
        if not endpoints:
            continue

        for endpoint in endpoints:
            endpoint_details = requests.get(endpoint['link']['href'], auth=auth, headers=headers, verify=False).json()['ERSEndPoint']
            last_seen = endpoint_details.get('lastSeenTime')
            
            if is_inactive(last_seen):
                print(f"Lösche inaktiven Endpunkt: {endpoint_details['mac']}")
                delete_endpoint(endpoint['id'])

if __name__ == "__main__":
    main()