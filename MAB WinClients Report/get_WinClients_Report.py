import csv


def value_exists(data_list, key, value):
    for entry in data_list:
        if key in entry and entry[key] == value:
            return True
    return False

def csv_to_dict(file_path):
    data_dict = []
    
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data_dict.append(row)
    
    return data_dict

def search_in_dict(data, key1, value1, key2, value2):
    results = []
    
    if key1 in data and data[key1] == value1 and key2 in data and data[key2] == value2:
        #print (f"Key1={entry[key1]} Key2={entry[key2]}")
        results.append(data)
        return True    
    
    return False

def dict_to_csv(data_list, file_path):
    if not data_list:
        return
    
    # Extrahiere die Schlüssel (Header) aus dem ersten Dictionary
    keys = data_list[0].keys()
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

    print(f'Data has been written to {file_path}')


#########################################
# MAIN
#########################################

# Global variables
import_file = "RADIUS_MAB_WinClients.csv" # Passe den Pfad entsprechend ann
export_MAB_WinClients = "MAB_WinClients.csv" # Passe den Dateipfad entsprechend an
export_DOT1X_WinClients = "DOT1X_WinClients.csv" # Passe den Dateipfad entsprechend an


result = csv_to_dict(import_file)
#print (result)
MAB_WinClients=[]
DOT1X_WinClients=[]
for line in result:
    #print (line)
    mac = line['Endpoint ID']

    search_line = search_in_dict(line, "Authentication Protocol", "EAP-TLS", 'Endpoint ID', mac)

    if search_line == True and value_exists(DOT1X_WinClients, "Endpoint ID", mac) == False:
        DOT1X_WinClients.append(line)
    else:
        if value_exists(MAB_WinClients, "Endpoint ID", mac) == False and line['Authentication Protocol'] != "EAP-TLS":
            MAB_WinClients.append(line)



for row in MAB_WinClients:
 print (row)

dict_to_csv(MAB_WinClients, export_MAB_WinClients)
dict_to_csv(DOT1X_WinClients, export_DOT1X_WinClients)
