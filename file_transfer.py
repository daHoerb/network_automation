from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_configure
import yaml
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config, netmiko_file_transfer

def copy_file(task, source, destination, server_username, server_password):
    task.run(
        task=napalm_configure,
        src=f"{server_username}:{server_password}@{source}",  # Server-Zugangsdaten hier einfügen
        dest=destination,
    )

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

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_UM.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)
# init Nornir Object
nr = InitNornir(config_file="config.yaml")
#hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!
#nr = nr.filter(hostname="10.108.240.48")
#filtered_hosts = nr.filter(lambda h: h.name.startswith("SWULOG6VH12") and h.site == "Wien")
nr = nr.filter(lambda host: "SWUMOG3VH12" in host.name)

result = nr.run(netmiko_file_transfer, name="File Transfer: ", source_file='/Users/hdinnobl/venv/dot1x-emergency/dot1x-emergency/dot1x-status.py', dest_file='guest-share/dot1x-status.py', overwrite_file=True)



for host, data in result.items():
    if data.failed:
        print(f"\nFehler beim Kopieren der Datei auf {host}: {data.exception}")
    else:
        print(f"\nDatei erfolgreich auf {host} kopiert.")