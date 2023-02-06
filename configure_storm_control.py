from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
#from nornir_netmiko.tasks import netmiko_send_config
from nornir_netmiko import netmiko_send_command, netmiko_send_config
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




def configure_storm_control(task):
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
    
    print(f'{host}: The following Access Interfaces will be configured:')
    print('--------------------------------------------')
    print(intf_list)
    
    # configure interfaces
    for intf_id in intf_list:
        intf_config = task.run(netmiko_send_config,name=host +": Set Interface command for " + intf_id ,config_commands=[
        "interface " + intf_id,
        "storm-control action shutdown",
        "storm-control broadcast level pps 1k",
        "storm-control multicast level pps 50k"]
        )
        print_result(intf_config)

    # check interfaces for err-disabled
    s = task.run(task=check_err_disabled_ports)
    err_disabled_portlist = s.result

    for intf_id in err_disabled_portlist:
        intf_config = task.run(netmiko_send_config,name=host +": Set Interface command for " + intf_id ,config_commands=[
        "interface " + intf_id,
        "spanning-tree bpduguard disable"]
        )
        print_result(intf_config)


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
#nr = nr.filter(hostname="172.20.254.119")
#filtered_hosts = nr.filter(lambda h: h.name.startswith("sw") and h.site == "Wien")
'''
# create filter to filter out devices with "sw" in hostname
sw_filter = F(hostname__contains="sw")

# apply filter to nornir inventory
filtered_hosts = nr.filter(sw_filter)

# print filtered hostnames
print("Filtered Hosts:")
for host in filtered_hosts.inventory.hosts.values():
    print(host.name)
'''
hosts = nr.inventory.hosts
print (hosts)

# try netmiko with textfsm
#result_ping = filter.run(task=netmiko_send_command, command_string="show ip interface brief", use_textfsm=True)


result = nr.run(task=configure_storm_control)
print_result(result)




failed_hosts = []
for host, result in result.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print (failed_hosts)