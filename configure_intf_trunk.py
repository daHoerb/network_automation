from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
#from nornir_netmiko.tasks import netmiko_send_config
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from ttp import ttp
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
import sys
import time
import yaml


def interface_uplink_config(task, config_file):
    
    r = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface switchport\"", command_string="sh interfaces switchport", use_textfsm=True)
    host=str(task.host)
    intf_dict = r.result
    
    # get uplinks
    intf_list = []
    for intf_info in intf_dict:
        if 'trunk' in intf_info['mode']:
            if 'member of bundle' in intf_info['mode']:
                continue
           
            intf_list.append(intf_info["interface"])
    host=str(task.host)

    print(f'{host}: The following Trunk Interfaces will be configured:')
    print('--------------------------------------------')
    print(intf_list)

    # get interface description
    s = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface description\"", command_string="sh interfaces description", use_textfsm=True)
    intf_descrip_list = s.result

    intf_descrip_dict = {}
    for intf_info in intf_descrip_list:
        intf_descrip_dict.update({intf_info["port"]:intf_info["descrip"]})

    # read config file
    with open(config_file) as f:
        commands_from_file = f.readlines()

    # configure interfaces
    for intf_id in intf_list:
        commands_4_netmiko = ["interface " + intf_id +"\n"] + commands_from_file
        intf_config = task.run(netmiko_send_config,name=(host +": Set Interface command for "+intf_id),config_commands=commands_4_netmiko)
        print (intf_config)


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
path = './Logs/intf_trunk_output.txt'
sys.stdout = Logger(path)

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_RH.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)

# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#nr = nr.filter(hostname="172.20.254.117")
#filtered_hosts = nr.filter(lambda h: h.name.startswith("sw") and h.site == "Wien")

results_intf_uplink = nr.run(task=interface_uplink_config, config_file="config/trunk_config.cfg")
print_result(results_intf_uplink)



failed_hosts = []
for host, result in results_intf_uplink.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")


print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)

