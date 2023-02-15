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


def interface_access_config(task, config_file):
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
        print (commands_4_netmiko)
        intf_config = task.run(netmiko_send_config,name=host +": Set Interface command for " + intf_id ,config_commands=commands_4_netmiko)
        print_result(intf_config)


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

'''
    eingabe = ''
    while (eingabe != "y"):
        eingabe = input(host+": do you want to re-configure ERR-DISABLED ports(y/n): [y] ")
        if eingabe == "n":
            exit("TERMINATE SCRIPT")
    
    for intf_id in intf_shut:
        config_set = ['interface ' + intf_id, 'shutdown', 'no description', 'no shut']
        print (intf_id)
        print (config_set)
        intf_config=task.run(task=netmiko_send_config, config_commands=config_set)
        print_result(intf_config)

'''

def bpduguard_config(task):

    host=str(task.host)

    r = task.run(netmiko_send_config, name='Set Global BPDU Guard default on all portfast ports', config_commands=[
        "default spanning-tree portfast bpduguard default"]
        )
    
    time.sleep(5)
    s = task.run(task=check_err_disabled_ports)
    err_disabled_portlist = s.result

    for intf_id in err_disabled_portlist:
        intf_config = task.run(netmiko_send_config,name=host +": Set Interface command for " + intf_id ,config_commands=[
        "interface " + intf_id,
        "spanning-tree bpduguard disable"]
        )
        print_result(intf_config)


def check_connection(task):
    try:
        r = task.run(netmiko_send_config, name='Check Connections', config_commands=["show user"])
        return f"{task.host} connection successful"
    except Exception as e:
        return f"{task.host} connection failed: {e}"



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
for host in hosts:
    print (host)

# try netmiko with textfsm
#result_ping = filter.run(task=netmiko_send_command, command_string="show ip interface brief", use_textfsm=True)


#result_intf_bpduguard = nr.run(task=bpduguard_config)
#results_err_intf = nr.run(task=check_err_disabled_ports)
#results_global = nr.run(task=global_config, config="config/vty_config.cfg")
#results_intf_access = nr.run(task=interface_access_config, config_file="config/access_config.cfg")
#results_intf_uplink = nr.run(task=interface_uplink_config, config_file="config/trunk_config.cfg")
results_save = nr.run(task=netmiko_save_config)
print_result(results_save)
#print_result(result_intf_bpduguard)
#print_result(results_err_intf)
#print_result(result_ping)
#print_result(results_global)
#print_result(results_intf_access)
#print_result(results_intf_uplink)

#check_err_disabled_result = nr.run(task=check_err_disabled_ports)

#print (result_connection)

failed_hosts = []
for host, result in results_save.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print (failed_hosts)
