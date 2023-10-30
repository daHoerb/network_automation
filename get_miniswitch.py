from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
import sys
import yaml


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
    
def get_miniswitch(task):


    #get mac table for access ports before configuration
    r = task.run(task=get_mac_address_access)
    mac_address_dict = r.result

    host=str(task.host)
    print ("Processing "+host+":")
  
    #get access port list
    s =task.run(task=get_access_ports)
    #print (s.result)
    access_ports = s.result

    # Count of MACs on Access Interface
    counter = 0
    intf_count = {}
    intf2vlanid_dict = {}

    for mac, intf_info in mac_address_dict.items():

        # if voice vlan the continue
        end = False
        for id in voice_vlanid:
            if intf_info[1]['vlan'] == id:
                #print (f"Found MAC in Restricted Vlan: Interface: {intf_info[0]['interface']} vlanid: {intf_info[1]['vlan']}")
                end = True
                break
        if end == True:
            continue
        

        intf = (intf_info[0]['interface'])
        #update = {"interface": counter+1}
        intf_vlanid = (intf_info[1]['vlan'])
        intf2vlanid_dict.update({intf: intf_vlanid})
        
        if intf not in intf_count:
            intf_count.update({intf: 1})

        else:
            intf_count[intf] = intf_count[intf]+1


    # Sortieren der Interface-Einträge
    intf_count = dict(sorted(intf_count.items()))


    # Print Interfaces with more than 1 MAC
    intf_fail = []
    for intf in intf_count:
        if intf_count[intf] > 1:
            print (f"WARNING!!! {host}: {intf} has {intf_count[intf]} MAC Addresses. Vlan ID: {intf2vlanid_dict[intf]}")
            intf_fail.append(intf)

    return intf_fail


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
path = './Logs/get_miniswitch.txt'
sys.stdout = Logger(path)

# Define Voice Vlanid
voice_vlanid = [101,104,980]

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_UM.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)


# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#nr = nr.filter(hostname="SWUSOG4VH12")
#nr = nr.filter(lambda host: "EGVH11" in host.name)
hosts = nr.inventory.hosts
print (hosts)


result_get_miniswitch = nr.run(task=get_miniswitch)
#print_result(result_get_miniswitch)

failed_hosts = []
for host, result in result_get_miniswitch.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print('The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)

