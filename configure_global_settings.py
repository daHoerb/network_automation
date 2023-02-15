from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
#from nornir_netmiko.tasks import netmiko_send_config
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
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
path = 'output.txt'
sys.stdout = Logger(path)

# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#nr = nr.filter(hostname="172.20.254.117")
#filtered_hosts = nr.filter(lambda h: h.name.startswith("sw") and h.site == "Wien")


# define the confing file which will be applied
results_global = nr.run(task=global_config, config="config/vty_config.cfg")
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

