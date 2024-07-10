from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Task, Result
from netmiko import ConnectHandler
import yaml
import sys
import time


def check_unauthenticated_ports_vlan(task, vlan_name):

    host=str(task.host)
    print (f"Processing {host}:")
    # Kommando zum Abrufen aller Authentication Sessions
    auth_command = "show authentication sessions"
    auth_result = task.run(
        task=netmiko_send_command,
        command_string=auth_command,
        use_textfsm=True
    )
    #print (auth_result[0].result)
    # Identifiziere unauthenticated Ports
    if "No sessions" in auth_result[0].result:
        return "Kein DOT1X aktiviert"

    unauthenticated_ports = []
    for session in auth_result[0].result:
        
        if session.get("status") in "Unauthenticated":
            unauthenticated_ports.append(session.get("interface"))
            
    
    if not unauthenticated_ports:
        return "Keine unauthenticated Ports gefunden."
    
    # Kommando zum Abrufen der VLAN-Informationen
    vlan_command = "show vlan brief"
    vlan_result = task.run(
        task=netmiko_send_command,
        command_string=vlan_command,
        use_textfsm=True
    )
    
    # Suche nach dem VLAN mit dem angegebenen Namen
    target_vlan_id = []
    for vlan in vlan_result[0].result:
        if vlan_name in vlan["name"]:
            target_vlan_id.append(vlan["vlan_id"])
            
            
    
    if target_vlan_id is []:
        return f"VLAN mit Namen '{vlan_name}' nicht gefunden."
    
    results = []
    #print (target_vlan_id)
    
    #print (f"Unauthicated Ports: {unauthenticated_ports}")
    for port in unauthenticated_ports:
        #print ((f"Port '{port}' ist unauthenticated."))
        results.append(f"Port '{port}' ist unauthenticated.")
        
        # Überprüfe den VLAN-Status für den unauthenticated Port
        switchport_command = f"show interfaces {port} switchport"
        switchport_result = task.run(
            task=netmiko_send_command,
            command_string=switchport_command,
            use_textfsm=True
        )
        
        if switchport_result[0].result:
            switchport_info = switchport_result[0].result[0]
            
            if "access" in switchport_info["mode"]:
               
                #print(switchport_info["access_vlan"])
                if switchport_info["access_vlan"] in target_vlan_id:
                    print(f"{host}: Port '{port}' ist im VLAN '{vlan_name}' (ID: {target_vlan_id}).")
                    results.append(f"Port '{port}' ist im VLAN '{vlan_name}' (ID: {target_vlan_id}).")
                else:
                    #print (f"Port '{port}' ist nicht im VLAN '{vlan_name}' (ID: {target_vlan_id}).")
                    results.append(f"Port '{port}' ist nicht im VLAN '{vlan_name}' (ID: {target_vlan_id}).")
            '''
            elif switchport_info["mode"] == "trunk":
                if target_vlan_id in switchport_info.get("trunking_vlans", []):
                    results.append(f"Port '{port}' ist ein Trunk-Port und erlaubt VLAN '{vlan_name}' (ID: {target_vlan_id}).")
                else:
                    results.append(f"Port '{port}' ist ein Trunk-Port, erlaubt aber nicht VLAN '{vlan_name}' (ID: {target_vlan_id}).")
            
            else:
                results.append(f"Konnte den VLAN-Status für Port '{port}' nicht bestimmen.")
            '''
        else:
            print (f"Konnte keine Switchport-Informationen für Port '{port}' abrufen.")
            results.append(f"Konnte keine Switchport-Informationen für Port '{port}' abrufen.")
        
        results.append("")  # Leerzeile für bessere Lesbarkeit
    #print (results)
    #return "\n".join(results)

def update_config_yaml(path_inventory_file):
    # Lade die vorhandene config.yaml-Datei
    with open("config.yaml", "r") as config_file:
        config_data = yaml.safe_load(config_file)

    # Aktualisiere den Pfad zur hosts.yaml-Datei
    config_data["inventory"]["options"]["host_file"] = path_inventory_file

    # Schreibe die aktualisierte Konfiguration zurück in die config.yaml-Datei
    with open("config.yaml", "w") as config_file:
        yaml.dump(config_data, config_file, default_flow_style=False)


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
path = 'Logs/get_unauthenticated_WinClientpPorts'
sys.stdout = Logger(path)

# Pfad zum Inventory File
path_inventory_file = 'Inventory/hosts_RM.yaml'  # Passe den Dateipfad entsprechend an
update_config_yaml(path_inventory_file)


# init Nornir Object
nr = InitNornir(config_file="config.yaml")

#nr = nr.filter(lambda host: "SWUSOG1VH41" in host.name)

hosts = nr.inventory.hosts
print (hosts)


results = nr.run(task=check_unauthenticated_ports_vlan, vlan_name="Win")
#print_result(results)


failed_hosts = []
for host, result in results.items():
    if result.failed:
        print(f"Task failed on host {host}: {result}")
        failed_hosts.append(host)
    else:
        print(f"Task succeeded on host {host}: {result.result}")

print ("\n")
print(f'{host}: The Task failed on the following Hosts:')
print('--------------------------------------------')
print (failed_hosts)