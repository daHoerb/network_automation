from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
import csv
import yaml
import json


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Fehler beim Laden der YAML-Datei: {e}")
            return None

myMAC = []

# Define the correct Core Switch
coreswitch = "SWUM0001"

nr = InitNornir(config_file="config.yaml")
nr = nr.filter(name=coreswitch)
result = nr.run(
    task=napalm_get,
    getters=["mac_address_table"]
)
# get mac table from Core Router
mac_table = result[coreswitch][0].result["mac_address_table"]


# create dict from mac table
mac_table_list=[]
for mac_info in mac_table:

    if mac_info["static"] == False:
        mac_table_list.append({"mac": mac_info["mac"], "vlan" : mac_info["vlan"]})
        print (mac_info)



# Laden der Identy Groups aus einem yaml file
file_path = 'IdentyGroups/UM_IdentyGroups.yaml'  # Passe den Dateipfad entsprechend an
data = load_yaml(file_path)
if data is None:
    print(json.dumps(data, indent=3))
    print ("File exist Error")
else:
    print (f'Loading {file_path} succesful')



# create file for import
with open('import_mab.csv', mode='w', newline='') as csv_file:
    fieldnames = ['MACAddress', 'EndPointPolicy', 'IdentityGroup', 'PortalUser.GuestType', 'Description']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for mac_info in mac_table_list:
        row = {}
        row["MACAddress"] = mac_info["mac"]
        print (mac_info["vlan"])
        if not mac_info["vlan"] in data or mac_info["vlan"] == None:
            print ("Key not found")
            continue

        if data[mac_info["vlan"]]["identy_group"] == None:
            print ("Identy Group not found")
            continue
        row["IdentityGroup"] = data[mac_info["vlan"]]["identy_group"]
        print (row)
        #print ("end of raw")
        writer.writerow(row)
