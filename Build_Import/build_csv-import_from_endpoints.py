from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
import csv
import yaml
import json
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from ttp import ttp
from nornir_utils.plugins.functions import print_result


        
def get_mac(host, intf):
    for element in list:
        #print (element['MACAddress'])
        if element['NAS-IP-Address'] == host and element['NAS-Port-Id'] == intf:
            #print (f"The MAC is {element['MACAddress']}")
            return element['MACAddress']
        
def vlan2identygroup(vlan_id):

    if vlan_id == None:
        return False  
    if int(vlan_id) not in data_identygroup:
        return None
    else:
        identygroup = data_identygroup[int(vlan_id)]['identy_group']
        #print (identygroup)
        return identygroup


        
def get_intf_vlan_fom_switch(task):
    r = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface switchport\"", command_string="sh interfaces switchport", use_textfsm=True)
    host=str(task.host)
    intf_dict = r.result

    s = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface\"", command_string="sh interfaces", use_textfsm=True)
    intf_sh_intf = s.result


    for element in list:
        #print (f"{host} sucht {element['NAS-IP-Address']}")
        if str(host) == element['NAS-IP-Address']:
            #print (intf_dict)
            search_intf = intf_dict[0]['interface'].replace("Gi", "GigabitEthernet")

            # Find Vlan ID
            for intf_info in intf_dict:
                #print (intf_info['interface'])
                search_intf = intf_info['interface'].replace("Gi", "GigabitEthernet")
                #print (f"search_intf: {search_intf}")
                #print (element['NAS-Port-Id'])
                if search_intf == element['NAS-Port-Id']:
                    print (f"{host}: Success: Found searched interface {element['NAS-Port-Id']}")
                    print (f"Access Vlan: {intf_info['access_vlan']}")
                    #print (f"description: {}")
                    mac = get_mac (host, search_intf)
                    
                    if vlan2identygroup(intf_info['access_vlan']) == False:
                        print (f"{mac} has not a Identy Group assigned")

                    # Find Port Description
                    for item in intf_sh_intf:
                        if item['interface'] == element['NAS-Port-Id']:
                            print (f"Port Description found: {item['description']}")
                            port_descr = item['description']
                    
                    new_entry = {'mac': mac, 
                                'identy_group': vlan2identygroup(intf_info['access_vlan']),
                                'vlanid': intf_info['access_vlan'],
                                'description': port_descr}
                                
                    
                    # Add Info to dict
                    dict2writeFile.append(new_entry)



#########################################
# LOADING OF FILES
#########################################

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Fehler beim Laden der YAML-Datei: {e}")
            return None


# Laden des Inventory aus einem yaml file
def load_inventory(file_path):
    data_inventory = load_yaml(file_path)
    if data_inventory is None:
        print(json.dumps(data_inventory, indent=3))
        print ("File exist Error")
        return None
    else:
        print (f'Loading {file_path} successful')
        return data_inventory

# Laden der Identy Groups aus einem yaml file
def load_identy(file_path):
    data_identygroup = load_yaml(file_path)
    if data_identygroup is None:
        
        print ("File exist Error")
        return None
    else:
        print (f'Loading {file_path} succesful')
        print(json.dumps(data_identygroup, indent=3))
        return data_identygroup


# Laden der Import CSV Files
def load_import_file(import_file):
    
    with open(import_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        
        for row in csv_reader:
            #print (row)
            newline = {}
            newline["MACAddress"] = row["MACAddress"]
            newline["ip"]=row["ip"]
            newline["NAS-IP-Address"] = row["NAS-IP-Address"]
            newline["NAS-Port-Id"] = row["NAS-Port-Id"]
            newline["OUI"] = row["OUI"]
            newline["FailureReason"] = row["FailureReason"]

            list.append(newline)
            line_count += 1
        print(f'Processed {line_count} lines.')

# create file for MAB Import
def write_mab_file(export_mab_file):
    with open(export_mab_file, mode='w', newline='') as csv_file:
        fieldnames = ['MACAddress', 'EndPointPolicy', 'IdentityGroup', 'PortalUser.GuestType', 'Description']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        print (f"Write File {export_mab_file}")
        line_count = 0
        for mac_info in dict2writeFile:
            row = {}
            row["MACAddress"] = mac_info["mac"]
            row["IdentityGroup"] = mac_info["identy_group"]

            if mac_info["identy_group"] == None:
                #print ("Identy Group not found")
                continue
            #print (row)
            #print ("end of raw")
            writer.writerow(row)
            line_count = line_count +1
        
        print(f'Processed {line_count} lines.')

def mac2vlanid(mac):
    for entry in dict2writeFile:
        if mac == entry['mac']:
            return entry['vlanid']        
    return None

def mac2description(mac):
    for entry in dict2writeFile:
        if mac == entry['mac']:
            return entry['description']        
    return None

# create file for dot1x Failed Authentications
def write_no_dot1x_file(export_no_dot1x_file):

    with open(export_no_dot1x_file, mode='w', newline='') as csv_file:
        fieldnames = ['MACAddress', 'ip', 'NAS-IP-Address', 'NAS-Port-Id', 'Description','OUI', 'FailureReason', 'Vlan-ID']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        print (f"Write File {export_no_dot1x_file}")
        writer.writeheader()
        
        line_count = 0
        for row in list:
            
            
            newline = dict(row)
            print (newline)

                
            newline['Vlan-ID'] = mac2vlanid(newline['MACAddress'])
            print (newline['Vlan-ID'])
                   
            if vlan2identygroup((newline['Vlan-ID'])) == False:
                print (f"There is no Idendity Group to this MAC found: {newline['MACAddress']} False")
                #newline['Description'] = mac2description(row['MACAddress'])
                #newline['Vlan-ID'] = mac2vlanid(row['MACAddress'])
                
                writer.writerow(newline)
                line_count = line_count + 1

            if vlan2identygroup((newline['Vlan-ID'])) == None:
                print (f"There is no Idendity Group to this MAC found: {newline['MACAddress']} None")
                newline['Description'] = mac2description(row['MACAddress'])
                    
                writer.writerow(newline)
                line_count = line_count + 1

        print(f'Processed {line_count} lines.')


def update_config_yaml(inventory_file):
    # Lade die vorhandene config.yaml-Datei
    with open("config.yaml", "r") as config_file:
        config_data = yaml.safe_load(config_file)

    # Aktualisiere den Pfad zur hosts.yaml-Datei
    config_data["inventory"]["options"]["host_file"] = inventory_file

    # Schreibe die aktualisierte Konfiguration zurück in die config.yaml-Datei
    with open("config.yaml", "w") as config_file:
        yaml.dump(config_data, config_file, default_flow_style=False)


#########################################
# MAIN
#########################################

# Global variables
list = []
dict2writeFile = []
import_file = "converted_profiler_endpoints.csv" # Passe den Pfad entsprechend an
inventory_file = '../Inventory/hosts_US.yaml'  # Passe den Dateipfad entsprechend an
identy_file = '../IdentyGroups/US_IdentyGroups.yaml'  # Passe den Dateipfad entsprechend an
export_mab_file = "import_mab.csv" # Passe den Dateipfad entsprechend an
export_no_dot1x_file = "no_dot1x.csv" # Passe den Dateipfad entsprechend an

# Update config.yaml file
update_config_yaml(inventory_file)

# init Nornir Object
nr = InitNornir(config_file='config.yaml')

data_inventory = load_inventory(inventory_file)
data_identygroup = load_identy(identy_file)
load_import_file(import_file)


def my_filter(host):
    # Hier kannst du deine eigenen Filterkriterien implementieren
    # Zum Beispiel: Gib nur Hosts zurück, die 'role' gleich 'router' haben
    #print (host)
    for element in list:
        #print (f"{host} sucht {element['NAS-IP-Address']}")
        if str(host) == element['NAS-IP-Address']:
            return True   
    else: return False

# Wende die Filterfunktion auf die Hosts an
filtered_hosts = nr.filter(filter_func=my_filter)


# Check if MAB Identy Group / vlan is available on switchport
print (filtered_hosts.inventory.hosts)

results = filtered_hosts.run(task=get_intf_vlan_fom_switch)

#print_result(results)
print ('dict2writeFile')
print (dict2writeFile)


failed_hosts = []
for host, result in results.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")


print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)


# create file for import
write_mab_file(export_mab_file)

# Create File for failed Dot1X Authentications
write_no_dot1x_file(export_no_dot1x_file)

