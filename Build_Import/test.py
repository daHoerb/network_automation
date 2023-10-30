import yaml

def update_config_yaml(inventory_file):
    # Lade die vorhandene config.yaml-Datei
    with open("../config.yaml", "r") as config_file:
        config_data = yaml.safe_load(config_file)

    # Aktualisiere den Pfad zur hosts.yaml-Datei
    config_data["inventory"]["options"]["host_file"] = inventory_file

    # Schreibe die aktualisierte Konfiguration zurück in die config.yaml-Datei
    with open("../config.yaml", "w") as config_file:
        yaml.dump(config_data, config_file, default_flow_style=False)


update_config_yaml('../Inventory/hosts_UP.yaml')