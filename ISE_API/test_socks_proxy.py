import socks
import socket
import requests

# Setze SOCKS5-Proxy-Einstellungen
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1084)
socket.socket = socks.socksocket

# Definiere die URL und die Anmeldeinformationen für den Zielserver
url = "https://10.208.81.202:9060/ers/config/endpointgroup?size=100&filter=name.CONTAINS.Drucker"
username = "nts_hed"
password = "A0Ae18oUHO"

## Führe die HTTP-Anfrage durch
response = requests.get(url, auth=(username, password), verify=False)  # `verify=False` deaktiviert SSL-Überprüfung

# Ausgabe der Antwort
print(response.text)


