import shutil
from nornir import InitNornir

# Please define the hosts file in config.yaml
# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#nr = nr.filter(hostname="10.208.60.36")


hosts = nr.inventory.hosts
for host in hosts:
    print (host)

# Definiere die Dateien, die kopiert werden sollen
#source_file = "C:\\Users\\hdinnobl\\Desktop\\SecureCRT\\Config\\Sessions\\AUVA\\UK\\SWUK0001.ini"
source_file = "C:/Users/hdinnobl/Desktop/SecureCRT/Config/Sessions/AUVA/UK/SWUK0001.INI"

for host in hosts:
    destination_file = f"C:/Users/hdinnobl/Desktop/SecureCRT/Config/Sessions/AUVA/UK/{host}.ini"
    print (destination_file)
    
    # Kopiere die Datei von der Quelle zum Ziel
    shutil.copy(source_file, destination_file)

    # Öffne die neue Datei im Schreibmodus
    with open(destination_file, "r+") as file:
        # Lese den gesamten Inhalt der Datei
        content = file.read()

        # Ersetze bestimmte Stellen im Inhalt mit neuen Variablen
        #hostname_ip = "10.208.60.1"
        
        content = content.replace("10.208.60.1", host)

        # Setze den Dateizeiger an den Anfang der Datei
        file.seek(0)

        # Schreibe den neuen Inhalt in die Datei
        file.write(content)

        # Schließe die Datei
        file.close()
    