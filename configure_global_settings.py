from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
import csv
import os
import pprint
import json
import sys
import time

def global_config(task, config):

    r = task.run(netmiko_send_config, name='Set Global Config via Configfile', config_file=config, read_timeout=0)
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

#==============================================================================
# ---- Main: Run Commands
#==============================================================================  

# write output stream to file
path = 'configure_global_settings_output.txt'
sys.stdout = Logger(path)

# init Nornir Object
nr = InitNornir(config_file="config.yaml")

hosts = nr.inventory.hosts
for host in hosts:
    print (host)


results_global = nr.run(task=global_config, config="config/global_config.cfg")
print_result(results_global)


failed_hosts = []
for host, result in results_save.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")


print('The Task failed on the following hosts:')
print('--------------------------------------------')
print (failed_hosts)
