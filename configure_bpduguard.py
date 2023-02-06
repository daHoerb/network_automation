from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
from netmiko import ConnectHandler

import sys
import time




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


result_intf_bpduguard = nr.run(task=bpduguard_config)
print_result(result_intf_bpduguard)


failed_hosts = []
for host, result in result_intf_bpduguard.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print (failed_hosts)
