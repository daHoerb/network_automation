import csv
import yaml
import json

import_file = "profiler_endpoints.csv"
file_path = '../Inventory/hosts_US.yaml'  # Passe den Dateipfad entsprechend an
dict = []


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Fehler beim Laden der YAML-Datei: {e}")
            return None
        
def ip2hostname(ip):
    for host, values in data.items():
        
        if ip == values['hostname']:
            print (values['hostname'])
            return host
        
    print (f"No Hostname to {ip} found")
    return "Hostname not found"




# Laden des Inevntory aus einem yaml file

data = load_yaml(file_path)
if data is None:
    print(json.dumps(data, indent=3))
    print ("File exist Error")
else:
    print (f'Loading {file_path} successful')


print (data)

with open(import_file, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    
    for row in csv_reader:
        #print (row)
        newline = {}
        newline["MACAddress"] = row["MACAddress"]
        newline["ip"]=row["ip"]
        newline["NAS-IP-Address"] = ip2hostname(row["NAS-IP-Address"])
        newline["NAS-Port-Id"] = row["NAS-Port-Id"]
        newline["OUI"] = row["OUI"]
        newline["FailureReason"] = row["FailureReason"]

        dict.append(newline)
        line_count += 1
    print(f'Processed {line_count} lines.')

#print (dict)
#print (csv_reader.fieldnames)


with open('converted_profiler_endpoints.csv', mode='w', newline='') as csv_file:
    fieldnames = ['MACAddress', 'ip', 'NAS-IP-Address', 'NAS-Port-Id', 'OUI', 'FailureReason']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for row in dict:
        print (row)
        #print ("end of raw")
        writer.writerow(row)
