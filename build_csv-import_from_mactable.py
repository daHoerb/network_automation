from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
import csv



myMAC = []

nr = InitNornir(config_file="config.yaml")
nr = nr.filter(name="SWUS0001")
result = nr.run(
    task=napalm_get,
    getters=["mac_address_table"]
)
# get mac table from Core Router
mac_table = result["SWUS0001"][0].result["mac_address_table"]


# create dict from mac table
mac_table_list=[]
for mac_info in mac_table:

    if mac_info["static"] == False:
        mac_table_list.append({"mac": mac_info["mac"], "vlan" : mac_info["vlan"]})
        print (mac_info)

# create dict for mab identy groups
vlan_2_identy_group={
    158: "MAB_LS-US-MT",
    905: "MAB_LS-US_ADSL2",
    903: "MAB_LS-US_ADSL_Service",
    173: "MAB_LS-US_ALOM",
    163: "MAB_LS-US_ASTRACONTROL",
    127: "MAB_LS-US_DATACASH",
    162: "MAB_LS-US_DICOM",
    61: "MAB_LS-US_PAT_MON_IBST",
    160: "MAB_LS-US_Roentgen",
    904: "MAB_LS-US_Siemens_Video",
    161: "MAB_LS-US_Steri",
    174: "MAB_LS-US_Video_Konferenz",
    74: "MAB_LS-US_ZLT",
    154: "MAB_LS-US_Zutritt",
    155: "MAB_US_Drucker",
    254: "MAB_US_GINA",
    148: "MAB_US_Phones",
    126: "MAB_LS_Videoaufruf",
    165: "MAB_LS-US_Infusion",
    970: "MAB_LS_US_Pat_IP_TV"
}




# create file for import
with open('import_mab.csv', mode='w', newline='') as csv_file:
    fieldnames = ['MACAddress', 'EndPointPolicy', 'IdentityGroup', 'PortalUser.GuestType', 'Description']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for mac_info in mac_table_list:
        row = {}
        row["MACAddress"] = mac_info["mac"]
        print (mac_info["vlan"])
        if not mac_info["vlan"] in vlan_2_identy_group:
            print ("Key not found")
            continue
        row["IdentityGroup"] = vlan_2_identy_group[mac_info["vlan"]]
        print (row)
        #print ("end of raw")
        writer.writerow(row)
