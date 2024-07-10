from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
import sys
import yaml

#Find mac on interface
def mac_on_intf(intf, mac_address_table):
    
    for entry in mac_address_table["mac_address_table"]:
        if entry['interface'] == intf:
            return entry['mac']
    
    return "No Mac found"


def get_haustechnik_ports(task, haustechnik_vlanid):
    r = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface switchport\"", command_string="sh interfaces switchport", use_textfsm=True)
    host=str(task.host)
    intf_dict = r.result

    # get access equal voice ports
    intf_list = []
    for intf_info in intf_dict:
      
        #print (intf_info)
        #print (type(intf_info['access_vlan']))
        if intf_info['access_vlan'] == "unassigned":
            continue

        if int(intf_info['access_vlan']) == haustechnik_vlanid and intf_info["mode"] == "down":
            intf_list.append(intf_info["interface"])
            print (f"{host}: Interface is DOWN with Haustechnik vlan {haustechnik_vlanid}: {intf_info['interface']}")
        
        if int(intf_info['access_vlan']) == haustechnik_vlanid and intf_info["mode"] != "down":
            intf_list.append(intf_info["interface"])
            print (f"{host}: Interface UP with Haustechnik vlan {haustechnik_vlanid}: {intf_info['interface']}")
    
    return Result(task.host, intf_list)
    


class Logger:

    def __init__(self, filename):
        self.console = sys.stdout
        self.file = open(filename, 'w')
 
    def write(self, message):
        self.console.write(message)
        self.file.write(message)
 
    def flush(self):
        self.console.flush()
        self.file.flush()

def update_config_yaml(path_inventory_file):
    # Lade die vorhandene config.yaml-Datei
    with open("config.yaml", "r") as config_file:
        config_data = yaml.safe_load(config_file)

    # Aktualisiere den Pfad zur hosts.yaml-Datei
    config_data["inventory"]["options"]["host_file"] = path_inventory_file

    # Schreibe die aktualisierte Konfiguration zurück in die config.yaml-Datei
    with open("config.yaml", "w") as config_file:
        yaml.dump(config_data, config_file, default_flow_style=False)

#==============================================================================
# ---- Main: Run Commands
#==============================================================================  

# write output stream to file
path = './Logs/get_haustechnik_ports.txt'
sys.stdout = Logger(path)

# Define Haustechnik Vlanid
haustechnik_vlanid = 62

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_RH.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)


# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#nr = nr.filter(hostname="SWUSOG4VH12")
#nr = nr.filter(lambda host: "BU112" in host.name)
hosts = nr.inventory.hosts
print (hosts)


result_get_haustechnik_ports = nr.run(task=get_haustechnik_ports, haustechnik_vlanid=haustechnik_vlanid)
#print_result(result_get_haustechnik_ports)

failed_hosts = []
for host, result in result_get_haustechnik_ports.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)

