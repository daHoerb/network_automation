from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
from netmiko import ConnectHandler

import sys
import time




def get_unauthenticated_ports(task):
    r = task.run(task=netmiko_send_command, command_string="show authentication sessions", use_textfsm=True)
    host=str(task.host)
    intf_list = r.result

    intf_unauth = []
    for intf_info in intf_list:
        if intf_info["status"] == "Unauth":
            intf_unauth.append(intf_info["interface"])
    
    print (f'{host}: Thefollowing Interfaces are UNAUTHENTICATED:')
    print ("---------------------------------------------------")
    print (intf_unauth)
    print ("")
    return intf_unauth


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
path = 'configure_bpduguard_output.txt'
sys.stdout = Logger(path)

# init Nornir Object
nr = InitNornir(config_file="config.yaml")

hosts = nr.inventory.hosts
for host in hosts:
    print (host)


results = nr.run(task=get_unauthenticated_ports)
print_result(results)


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