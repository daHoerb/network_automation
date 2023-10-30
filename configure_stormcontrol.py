from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
import sys
import time
import yaml


def check_err_disabled_ports(task):
    r = task.run(task=netmiko_send_command, command_string="sh interfaces status", use_textfsm=True)
    host=str(task.host)
    err_intf_list = r.result
    intf_shut = []
    for intf_info in err_intf_list:
        #if intf_info["status"] == "notconnect":
        if intf_info["status"] == "err-disabled":
            intf_shut.append(intf_info["port"])
        
    print(f'{host}: The following Interfaces are err-disabled:')
    print('--------------------------------------------')
    print(intf_shut)

    return Result(
        host=task.host,
        result=(intf_shut))


def stormcontrol_config(task):

    r = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface switchport\"", command_string="sh interfaces switchport", use_textfsm=True)
    host=str(task.host)
    intf_dict = r.result
    
    # get access ports
    intf_list = []
    intf_desc_dict = {}
    for intf_info in intf_dict:
        if intf_info['mode'] == 'down' and 'trunk' not in intf_info['admin_mode'] or 'access' in intf_info['mode']:
            if 'member of bundle' in intf_info['mode']:
                port_channel_raw_string = intf_info['mode'].split()
                port_channel = port_channel_raw_string[-1][:-1]
                intf_list.append(port_channel)
                intf_list = set (intf_list)
         
            intf_list.append(intf_info["interface"])
    
    print(f'{host}: The following Access Interfaces will be configured for storm-control:')
    print('--------------------------------------------')
    print(intf_list)
    
    for intf_id in intf_list:
        intf_config = task.run(netmiko_send_config,name=host +": Set Interface command for " + intf_id ,config_commands=[
        "interface " + intf_id,
        "storm-control broadcast level pps 1k",
        "storm-control multicast level pps 50k",
        "storm-control action shutdown"]
        )
        print_result(intf_config)

    time.sleep(5)

    # check err-disabled ports
    s = task.run(task=check_err_disabled_ports)
    err_disabled_portlist = s.result

    # reconfigure err-disabled ports
    for intf_id in err_disabled_portlist:
        intf_config = task.run(netmiko_send_config,name=host +": Set Interface command for " + intf_id ,config_commands=[
        "interface " + intf_id,
        "no storm-control broadcast level pps 1k",
        "no storm-control multicast level pps 50k",
        "no storm-control action shutdown"]
        )
        print_result(intf_config)

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
path = './Logs/intf_stormcontrol_output.txt'
sys.stdout = Logger(path)

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_RH.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)

# init Nornir Object
nr = InitNornir(config_file="config.yaml")

hosts = nr.inventory.hosts
for host in hosts:
    print (host)


result_intf_stormcontrol = nr.run(task=stormcontrol_config)
print_result(result_intf_stormcontrol)


failed_hosts = []
for host, result in result_intf_stormcontrol.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)
