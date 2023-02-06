from nornir import InitNornir
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result


#==============================================================================
# ---- Main: Run Commands
#==============================================================================  


# init Nornir Object
nr = InitNornir(config_file="config.yaml")

hosts = nr.inventory.hosts
for host in hosts:
    print (host)

results_save = nr.run(task=netmiko_save_config)
print_result(results_save)

failed_hosts = []
for host, result in result_intf_bpduguard.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print('The Task failed on the following hosts:')
print('--------------------------------------------')
print (failed_hosts)