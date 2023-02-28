from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result
import sys


def get_snmp_info(task):
    host=str(task.host)

    try:
        r = task.run(napalm_get, name='get snmpv2 info from host', getters="get_snmp_information")
        snmp_communities=r.result["get_snmp_information"]["community"].keys()      
       
    except Exception as e:
        return f"{task.host} connection failed: {e}"

    try:
        
        if snmp_communities == []:
            return   
        for community in snmp_communities:
            print ("Try to delete the following Community "+community)
            community = str(community)
            snmp_config = task.run(netmiko_send_config,name=host +": Delete SNMP Community " + community, config_commands=["no snmp-server community "+community])
            print_result(snmp_config)
        return ("Deleted SNMP Communities!")

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

# write output stream to file
path = 'output.txt'
sys.stdout = Logger(path)


# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#filter = nr.filter(hostname="172.20.254.16")
#filtered_hosts = nr.filter(lambda h: h.name.startswith("sw") and h.site == "Wien")

hosts = nr.inventory.hosts
#print (hosts)



results = nr.run(task=get_snmp_info)
print_result (results)
#print (snmp_communities)


failed_hosts = []
for host, result in results.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print("The Task failed on the following Hosts:")
print('--------------------------------------------')
print (failed_hosts)      