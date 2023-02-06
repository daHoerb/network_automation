from nornir import InitNornir
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from ttp import ttp
#from nornir.plugins.tasks import commands
from nornir_utils.plugins.functions import print_result

# init Nornir Object
nr = InitNornir(config_file="config.yaml")

results_save = nr.run(task=netmiko_save_config)
print_result(results_save)


failed_hosts = []
for host, result in results_save.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print (failed_hosts)