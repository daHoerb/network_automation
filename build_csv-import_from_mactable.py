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
coreswitch = "SWRH0001"

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

# create dict for mab identy groups in LS
vlan_2_identy_group_LS={
    158: "MAB_LS-US-MT",
    905: "MAB_LS-US_ADSL2",
    903: "MAB_LS-US_ADSL_Service",
    173: "MAB_LS-US_ALOM",
    163: "MAB_LS-US_ASTRACONTROL",
    127: "MAB_LS-US_DATACASH",
    162: "MAB_LS-US_DICOM",
    61: "MAB_LS-US_PAT_MON_IBST",
    160: "MAB_LS-US_Roentgen",
    904: "MAB_LS-US_Siemens_Video",
    161: "MAB_LS-US_Steri",
    174: "MAB_LS-US_Video_Konferenz",
    74: "MAB_LS-US_ZLT",
    154: "MAB_LS-US_Zutritt",
    155: "MAB_US_Drucker",
    254: "MAB_US_GINA",
    148: "MAB_US_Phones",
    126: "MAB_LS_Videoaufruf",
    165: "MAB_LS-US_Infusion",
    970: "MAB_LS_US_Pat_IP_TV"
}

vlan_2_identy_group_RT={
    46: "MAB_RT_PKE",
    47: "MAB_RT_GINA",
    50: "MAB_RT_Zeiterfassung",
    52: "MAB_RT_TK",
    126: "MAB_TK_Videoaufruf",
    127: "MAB_RT_Datacash",
    148: "MAB_RT_PKE_alt",
    200: "MAB_TK_PRIMA",
    242: "MAB_RT_Drucker",
    247: "MAB_RT_Phone",
    253: "MAB_RT_DosisMes",
    254: "MAB_RT_MT",
    255: "MAB_RT_ALOM",
    902: "MAB_RT_LUFU",
    905: "MAB_RT_IAC-BOX_TA",
    970: "MAB_RT_PAT_IP_TV",
    980: "MAB_RT_Lichtruf"
}

# Laden der Identy Groups aus einem yaml file
file_path = 'IdentyGroups/RH_IdentyGroups.yaml'  # Passe den Dateipfad entsprechend an
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
