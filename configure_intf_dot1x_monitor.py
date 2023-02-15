from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
import sys
import time
from deepdiff import DeepDiff


def get_mac_address_access(task):
    host=str(task.host)
    s = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface switchport\"", command_string="sh interfaces switchport", use_textfsm=True)
    intf_dict = s.result
    #print (s.result)
    
    #get access ports
    t = task.run(task=get_access_ports)
    intf_access_list=t.result
    
    # get mac table
    r = task.run(napalm_get, getters=['get_mac_address_table'])
    get_mac_address_table = r.result['get_mac_address_table']
    
    mac_address_dict = {}
    for intf_info in get_mac_address_table:
        mac = intf_info['mac']
        interface = intf_info['interface']
        vlan = intf_info['vlan']
        if interface in intf_access_list:
            mac_address_dict.update({mac : [{"interface" : interface},{"vlan" : vlan}]})
    
    return Result(task.host, mac_address_dict)


def get_access_ports(task):
    r = task.run(task=netmiko_send_command, name="get parsed data from \"sh interface switchport\"", command_string="sh interfaces switchport", use_textfsm=True)
    host=str(task.host)
    intf_dict = r.result

    # get access ports
    intf_list = []
    for intf_info in intf_dict:
        if intf_info['mode'] == 'down' and 'trunk' not in intf_info['admin_mode'] or 'access' in intf_info['mode']:
            if 'member of bundle' in intf_info['mode']:
                port_channel_raw_string = intf_info['mode'].split()
                port_channel = port_channel_raw_string[-1][:-1]
                intf_list.append(port_channel)
                intf_list = set (intf_list)
         
            intf_list.append(intf_info["interface"])
    
    return Result(task.host, intf_list)
    
def dot1x_monitor_config(task):


    #get mac table for access ports before configuration
    r = task.run(task=get_mac_address_access)
    mac_address_dict_before = r.result

    host=str(task.host)
    print ("Processing "+host+" for dot1x")
  
    #get access port list
    s =task.run(task=get_access_ports)
    #print (s.result)
    access_ports = s.result

    print(f'{host}: The following Access Interfaces will be configured:')
    print('--------------------------------------------')
    print(access_ports)
    '''
    eingabe = ''
    while (eingabe != "y"):
        eingabe = input(host+": do you want to configure ports (y/n): [y] ")
        if eingabe == "n":
            exit("TERMINATE SCRIPT")
    '''
    # configure interfaces
    for intf_id in access_ports:
        intf_config = task.run(netmiko_send_config,name=(host +": Set Interface command for "+intf_id),config_commands=[
            "interface "+ intf_id,
            "access-session port-control auto"]
        )
        print_result(intf_config)

    time.sleep(70)

    # get mac table for access ports after configuarion
    t = task.run(task=get_mac_address_access)
    mac_address_dict_after = t.result

    # check missing mac addresses
    print ("*"*100)
    ddiff = DeepDiff(mac_address_dict_before, mac_address_dict_after, verbose_level=2)
    print(ddiff)
    print ("-"*100)
    
    # get interfaces from missing mac addresses
    intf_remove_config = []
    if bool(ddiff) is True:
        for items in ddiff["dictionary_item_removed"].items():
            interface = items[1][0]["interface"]
            intf_remove_config.append(items[1][0]["interface"])
            print (f"{host}: WARNING! missing MAC on {interface}")
    else:
        print ("all MAC Addresses found")    
    
            
        
    # remove configure interfaces
    for intf_id in intf_remove_config:
        print ("Remove config from "+intf_id)
        intf_config = task.run(netmiko_send_config,name=(host +": Set Interface command for "+intf_id),config_commands=[
            "interface "+ intf_id,
            "no access-session port-control auto"]
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
path = 'output.txt'
sys.stdout = Logger(path)

# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#nr = nr.filter(hostname="SWUSOG4VH12")
hosts = nr.inventory.hosts
print (hosts)


result_intf_dot1x_monitor = nr.run(task=dot1x_monitor_config)
print_result(result_intf_dot1x_monitor)

failed_hosts = []
for host, result in result_intf_dot1x_monitor.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print(f'{host}: The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)

