import shutil
from nornir import InitNornir
import json
import yaml



def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Fehler beim Laden der YAML-Datei: {e}")
            return None


#####################
# MAIN
####################


# Definiere die Dateien, die kopiert werden sollen
#source_file = "C:\\Users\\hdinnobl\\Desktop\\SecureCRT\\Config\\Sessions\\AUVA\\UK\\SWUK0001.ini"
file_path = 'Inventory/hosts_UB.yaml'  # Passe den Dateipfad entsprechend an
host_copy = "SWUB0001"
ip_copy = "10.108.95.254"
source_file = f"/Users/hdinnobl/Library/Application Support/VanDyke/SecureCRT/Config/Sessions/AUVA/UB/{host_copy}.ini"

data_inventory = load_yaml(file_path)

if data_inventory is None:
    print(json.dumps(data_inventory, indent=3))
    print ("File exist Error")
else:
    print (f'Loading {file_path} successful')

for host, item in data_inventory.items():
    ip = (item['hostname'])
    destination_file = f"/Users/hdinnobl/Library/Application Support/VanDyke/SecureCRT/Config/Sessions/AUVA/UB/{host}.ini"
    print (destination_file)
    
    # Kopiere die Datei von der Quelle zum Ziel
    shutil.copy(source_file, destination_file)

    # Öffne die neue Datei im Schreibmodus
    with open(destination_file, "r+") as file:
        # Lese den gesamten Inhalt der Datei
        content = file.read()

        # Ersetze bestimmte Stellen im Inhalt mit neuen Variablen
        #hostname_ip = "10.208.60.1"
        #print (f"Hostname={host_copy}   IP={host}")
        content = content.replace(host_copy, host)
        content = content.replace(ip_copy, ip)

        # Setze den Dateizeiger an den Anfang der Datei
        file.seek(0)

        # Schreibe den neuen Inhalt in die Datei
        file.write(content)

        # Schließe die Datei
        file.close()
