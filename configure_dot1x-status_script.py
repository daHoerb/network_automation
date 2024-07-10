from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
#from nornir_netmiko.tasks import netmiko_send_config
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config, netmiko_multiline
from ttp import ttp
#from nornir.plugins.tasks import commands
from nornir_utils.plugins.functions import print_result
#from nornir.plugins.functions.text import print_result
#from nornir.plugins.tasks.networking import napalm_get
#from nornir.plugins.tasks.networking import netmiko_send_command
#from nornir.plugins.tasks.networking.netmiko_send_config import netmiko_send_config
from nornir.core.task import Task, Result
from netmiko import ConnectHandler
import csv
import os
import pprint
import json
import sys
import time
import yaml


def global_config(task, config):

    with open(config, 'r') as file:
        config_lines = file.readlines()

    r = task.run(netmiko_send_config, name='Set Global Config via Configfile', config_file=config, read_timeout=10)
    print_result(r)

def global_command(task, command):

    r = task.run(netmiko_send_command, name='Send command', command_string = command)
    print_result(r)

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
path = './Logs/global_config.txt'
sys.stdout = Logger(path)

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_UG.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)
# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#nr = nr.filter(hostname="10.108.240.48")
#filtered_hosts = nr.filter(lambda h: h.name.startswith("SWRWLT011") and h.site == "Wien")
#nr = nr.filter(lambda host: "KG1VH21" in host.name)


# define the confing file which will be applied
#command = "ip scp server enable"
#results_global = nr.run(task=global_command, command=command)
results_global = nr.run(task=global_config, config="config/scp_server_enable.cfg")
print_result(results_global)


failed_hosts = []
for host, result in results_global.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)


results_global = nr.run(task=global_config, config="config/dot1x-status.cfg")
print_result(results_global)


failed_hosts = []
for host, result in results_global.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)