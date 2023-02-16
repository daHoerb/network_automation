import os
import logging
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_napalm.plugins.tasks.napalm_configure import napalm_configure
from nornir_netmiko import netmiko_send_command, netmiko_send_config, netmiko_save_config


BACKUP_DIR = "backups/"

nr = InitNornir(config_file="config.yaml")

def create_backups_dir():
    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)

def save_config_to_file(method, hostname, config):
    filename =  f"{hostname}-{method}.cfg"
    with open(os.path.join(BACKUP_DIR, filename), "w") as f:
        f.write(config)

def get_netmiko_backups():
    backup_results = nr.run(
        task=netmiko_send_command, 
        command_string="show run"
        )

    for hostname in backup_results:
        save_config_to_file(
            method="netmiko",
            hostname=hostname,
            config=backup_results[hostname][0].result,
        )

def get_napalm_backups():
    backup_results = nr.run(task=napalm_get, getters=["config"])

    for hostname in backup_results:
        config = backup_results[hostname][0].result["config"]["startup"]
        save_config_to_file(method="napalm", hostname=hostname, config=config)

def main():
    create_backups_dir()
    #get_netmiko_backups()
    get_napalm_backups()

if __name__ == "__main__":
    main()