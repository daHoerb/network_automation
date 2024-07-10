from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
import sys
import yaml



def get_static_access_ports(task):
    r = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface description\"", command_string="sh interfaces description", use_textfsm=True)
    host=str(task.host)
    intf_dict = r.result

    # get access ports
    intf_list = []
    for intf_info in intf_dict:

        # check for non-access ports
        if "Vl" in intf_info["port"] or  "Gi0" in intf_info["port"] or "Gi1/1" in intf_info["port"] or "Po" in intf_info["port"] or "Ap" in intf_info["port"]:
            continue
        
        # identify dot1x disables ports
        if '***STATIC***' in intf_info['descrip']:
            print(f"{host}: Interface: {intf_info['port']} is DOT1X DISABLED")
            intf_list.append(intf_info["port"])
    
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
path = './Logs/get_static_access_ports.txt'
sys.stdout = Logger(path)

# Define Voice Vlanid
voice_vlanid = [148]

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_UM.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)


# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#nr = nr.filter(hostname="SWUSOG4VH12")
#nr = nr.filter(lambda host: "KGVH21" in host.name)
hosts = nr.inventory.hosts
print (hosts)


result_get_miniswitch = nr.run(task=get_static_access_ports)
#print_result(result_get_miniswitch)

failed_hosts = []
for host, result in result_get_miniswitch.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)

