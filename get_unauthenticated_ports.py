from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
from netmiko import ConnectHandler
import yaml
import sys
import time




def get_unauthenticated_ports(task):
    r = task.run(task=netmiko_send_command, command_string="show authentication sessions", use_textfsm=True)
    host=str(task.host)
    intf_list = r.result
    #print (intf_list)
    
    intf_unauth = []
    for intf_info in intf_list:
        #if intf_info["status"] == "notconnect":
        if intf_info["status"] == "Unauth":
            intf_unauth.append(intf_info["interface"])
            #print(intf_info["interface"])
        
    print(f'{host}: The following Interfaces are Unauthenticated:')
    print('--------------------------------------------')
    print(intf_unauth)

    return (intf_unauth)

def update_config_yaml(path_inventory_file):
    # Lade die vorhandene config.yaml-Datei
    with open("config.yaml", "r") as config_file:
        config_data = yaml.safe_load(config_file)

    # Aktualisiere den Pfad zur hosts.yaml-Datei
    config_data["inventory"]["options"]["host_file"] = path_inventory_file

    # Schreibe die aktualisierte Konfiguration zurück in die config.yaml-Datei
    with open("config.yaml", "w") as config_file:
        yaml.dump(config_data, config_file, default_flow_style=False)


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

#==============================================================================
# ---- Main: Run Commands
#==============================================================================  

# write output stream to file
path = 'Logs/get_unauthenticated_ports'
sys.stdout = Logger(path)

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_LG.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)


# init Nornir Object
nr = InitNornir(config_file="config.yaml")

#nr = nr.filter(lambda host: "VH12" in host.name)

hosts = nr.inventory.hosts
print (hosts)


results = nr.run(task=get_unauthenticated_ports)
#print_result(results)


failed_hosts = []
for host, result in results.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print(f'{host}: The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)