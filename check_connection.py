from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
import sys




def check_connection(task):
    try:
        r = task.run(netmiko_send_config, name='check connections to host', config_commands=["do show user"])
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


# try connection and login
results = nr.run(task=check_connection)
#print_result(result_connection)

#print (result_connection)
failed_hosts = []
for host, result in results.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")


print (failed_hosts)

