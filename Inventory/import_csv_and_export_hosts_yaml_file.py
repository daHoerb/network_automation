import csv
import yaml
import json




# Öffnen Sie die CSV-Datei
with open('hosts_UB.csv', 'r') as f:
    reader = csv.reader(f)
    data = [row for row in reader]

# Erstellen Sie eine leere Liste, um die Host-Informationen zu speichern
hosts = {}

# Iterieren Sie durch die CSV-Daten und erstellen Sie ein dict pro Zeile
for row in data[1:]:
    row_data = row[0].split(";")
    column_0 = row_data[0]
    column_1 = row_data[1]
    print (row_data)
    host_values = {
        'hostname': column_1,
        'port': 22,
        'platform': "ios"
    }
    hosts.update({column_0:host_values})

#print ((hosts))
# Konvertieren Sie die Liste in ein YAML-Format und speichern Sie es in einer Datei
with open('hosts_UB.yaml', 'w') as f:
    yaml.dump(hosts, f)