from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
import sys


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
#nr = nr.filter(hostname="172.20.254.117")
#filtered_hosts = nr.filter(lambda h: h.name.startswith("sw") and h.site == "Wien")

hosts = nr.inventory.hosts
for host in hosts:
    print (host)


results_intf_access = nr.run(task=interface_access_config, config_file="config/access_config.cfg")
print_result(results_intf_access)


failed_hosts = []
for host, result in results_intf_access.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)

