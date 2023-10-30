import yaml
import json
import requests
from decouple import config


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Fehler beim Laden der YAML-Datei: {e}")
            return None


def get_identity_groups(api_base_url, username, password):
    
    # Endpoint-URL für die Identitätsgruppen
    url = f"{api_base_url}/ers/config/endpointgroup"
    print ('establish connection to '+url)

    # Header für die API-Autorisierung
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Authentifizierung mit Benutzername und Passwort
    auth = (username, password)

    # Proxy-Konfiguration mit Authentifizierung
    proxies = {
        'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
        'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
    } 

    print (proxies)
    print (proxy_port)
#        'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
    try:

        identity_groups = []
        while url:
            # HTTP GET-Anfrage senden mit Proxy-Konfiguration
            response = requests.get(url, headers=headers, auth=auth, proxies=proxies, verify=False)
        
            # Überprüfen, ob die Anfrage erfolgreich war
            if response.status_code == 200:
                # JSON-Daten aus der API-Antwort extrahieren
                data = response.json()
                identity_groups.extend(data['SearchResult']['resources'])
            else:
                print(f"Fehler bei der API-Anfrage. Statuscode: {response.status_code}")

            # Nächste Seite abrufen, falls verfügbar
            
            if 'nextPage' in data['SearchResult']:
                url = data['SearchResult']['nextPage']['href']
                print ('Next Page found: '+url)

            else:
                    url = None
            
        return identity_groups

    
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Verbindung zur API: {e}")

    return None

def get_authentication_profiles(api_base_url):
    
    # Endpoint-URL für die Authorization Profiles
    url = f"{api_base_url}/ers/config/authorizationprofile"
    print ('establish connection to '+url)

    # Header für die API-Autorisierung
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Authentifizierung mit Benutzername und Passwort
    auth = (username, password)

    # Proxy-Konfiguration mit Authentifizierung
    proxies = {
        'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
        'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
    } 

    try:

        authentication_profiles = []
        while url:
            # HTTP GET-Anfrage senden mit Proxy-Konfiguration
            response = requests.get(url, headers=headers, auth=auth, proxies=proxies, verify=False)
        
            # Überprüfen, ob die Anfrage erfolgreich war
            if response.status_code == 200:
                # JSON-Daten aus der API-Antwort extrahieren
                data = response.json()
                authentication_profiles.extend(data['SearchResult']['resources'])
            else:
                print(f"Fehler bei der API-Anfrage. Statuscode: {response.status_code}")
                #print (json.dumps(data, indent=4))
                data['SearchResult'] = {}

            # Nächste Seite abrufen, falls verfügbar
            
            if 'nextPage' in data['SearchResult']:
                url = data['SearchResult']['nextPage']['href']
                print ('Next Page found: '+url)

            else:
                    url = None
            
        return authentication_profiles

    
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Verbindung zur API: {e}")

    return None

# Idendy Groups auf der ISE anlegen
def pushIdentyGroups(api_base_url, name, description):
# Endpoint-URL für die Identitätsgruppen
    url = f"{api_base_url}/ers/config/endpointgroup"
    print ('establish connection to '+url)

    # Header für die API-Autorisierung
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Authentifizierung mit Benutzername und Passwort
    auth = (username, password)

    # Proxy-Konfiguration mit Authentifizierung
    proxies = {
        'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
        'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
    }
    payload = json.dumps({
        "EndPointGroup": {
            "name": name,
            "description": description
        }
    })

    try:
        response = requests.post(url, headers=headers, auth=auth, proxies=proxies, data=payload, verify=False)
            
        # Überprüfen, ob die Anfrage erfolgreich war
        if response.status_code == 201:
            # JSON-Daten aus der API-Antwort extrahieren
            print (f"Identy Group created {name} succesful")
            
        else:
            print(f"Fehler bei der API-Anfrage. Statuscode: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Verbindung zur API: {e}")

# Authentication Profiles auf der ISE anlegen
def pushAuthenticationProfiles(api_base_url, name, description, vlan_id, voicedomain=False):
# Endpoint-URL für die Authorization Profile
    url = f"{api_base_url}/ers/config/authorizationprofile"
    print ('establish connection to '+url)

    # Header für die API-Autorisierung
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    # Authentifizierung mit Benutzername und Passwort
    auth = (username, password)

    # Proxy-Konfiguration mit Authentifizierung
    proxies = {
        'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
        'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
    }
    payload = json.dumps(
    {
        "AuthorizationProfile": {
            "name": name,
            "description": description,
            "accessType": "ACCESS_ACCEPT",
            "authzProfileType": "SWITCH",
            "voiceDomainPermission": voicedomain,
            "reauth": {
                "timer": 28800,
                "connectivity": "RADIUS_REQUEST"
            },
            "vlan": {
                "nameID": vlan_id,
                "tagID": 1
            }
        }
    })
    print (payload)

    try:
        response = requests.post(url, headers=headers, auth=auth, proxies=proxies, data=payload, verify=False)
            
        # Überprüfen, ob die Anfrage erfolgreich war
        if response.status_code == 201:
            # JSON-Daten aus der API-Antwort extrahieren
            print (f"Authentication Profile  {name} created succesful")
            
        else:
            print(f"Fehler bei der API-Anfrage. Statuscode: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Verbindung zur API: {e}")

#==============================================================================
# ---- Main: Run Commands
#==============================================================================  

# Laden der Identy Groups auseinem yaml file
file_path = '../IdentyGroups/UM_IdentyGroups.yaml'  # Passe den Dateipfad entsprechend an
data = load_yaml(file_path)
if data is None:
    print(json.dumps(data, indent=3))
    print ("File exist Error")
else:
    print (f'Loading {file_path} succesful')

#print (data.items())
# Hole Werte aus der dotenv
api_base_url = config("api_base_url")
username = config("username")
password = config("password")
proxy_host = config("proxy_host")
proxy_port =config("proxy_port")
proxy_username = config("proxy_username")
proxy_password = config("proxy_password")


# Beispielaufruf 
'''
api_base_url = 'https://10.208.81.202:9060'  # Passe die API-Basis-URL entsprechend an
username = 'nts_hed'  # Passe den Benutzernamen entsprechend an
password = 'A0Ae18oUHO'  # Passe das Passwort entsprechend an
proxy_host = 'localhost'  # Passe den Proxy-Host entsprechend an
proxy_port = '60081'  # Passe den Proxy-Port entsprechend an
proxy_username = 'hdinnobl'  # Passe den Proxy-Benutzernamen entsprechend an
proxy_password = 'Om8)-Xj9UZ%w'  # Passe das Proxy-Passwort entsprechend an
'''
print ("Processing...   ISE DATEN WERDEN ABGEFRAGT:")
identity_groups = get_identity_groups(api_base_url, username, password)
authentication_profiles = get_authentication_profiles(api_base_url)


# Neue Liste erstellen erstellen
new_groups = []
new_authorization_profiles = []

for vlan_id, attribute  in data.items():
        new_groups.append(attribute['identy_group'])
        new_authorization_profiles.append(attribute['authorization_profile'])
        
# Überprüfen ob Identy Group bereits existiert
for group in identity_groups:
    if group['name'] in new_groups or group['name'] == "None":
            print (f'{group["name"]} already exist')
            new_groups.remove(group["name"])

print("Processing...  Identitätsgruppen werden angelegt:")
# Post der Identy Groups auf die ISE
for vlan_id, attribute  in data.items():
    if attribute['identy_group'] in new_groups and attribute['identy_group'] is not None:
        print (f"vlan_id={vlan_id} name={attribute['identy_group']}")
        name = attribute['identy_group']
        description = str(vlan_id)

        pushIdentyGroups(api_base_url, name, description)



# Überprüfen ob Authentication Profile bereits existiert
for profile in authentication_profiles:
    if profile['name'] in new_authorization_profiles:
            print (f'Profile for {profile["name"]} already exist')
            new_authorization_profiles.remove(profile["name"])

print ("Processing...  Authorization Profile werden angelegt:")
# Post der Authentication Profiles auf die ISE
for vlan_id, attribute  in data.items():
    if attribute['authorization_profile'] in new_authorization_profiles and attribute['authorization_profile'] is not None:
        #name = "vlan_"+vlan_id
        name = attribute['authorization_profile']
        description = "vlan "+str(vlan_id)

        if attribute.get("voiceDomainPermission") is not None:
            voicedomain = attribute['voiceDomainPermission']
            pushAuthenticationProfiles(api_base_url, name, description, vlan_id, voicedomain)         
        else:
            pushAuthenticationProfiles(api_base_url, name, description, vlan_id)
        

   
