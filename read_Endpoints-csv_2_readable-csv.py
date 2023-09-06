import csv

import_file = "profiler_endpoints.csv"
dict = []

with open(import_file, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    
    for row in csv_reader:
        #print (row)
        newline = {}
        newline["MACAddress"] = row["MACAddress"]
        newline["ip"]=row["ip"]
        newline["NAS-IP-Address"] = row["NAS-IP-Address"]
        newline["NAS-Port-Id"] = row["NAS-Port-Id"]
        newline["OUI"] = row["OUI"]
        newline["FailureReason"] = row["FailureReason"]

        dict.append(newline)
        line_count += 1
    print(f'Processed {line_count} lines.')

#print (dict)
#print (csv_reader.fieldnames)


with open('2023-06-27_converted_profiler_endpoints.csv', mode='w', newline='') as csv_file:
    fieldnames = ['MACAddress', 'ip', 'NAS-IP-Address', 'NAS-Port-Id', 'OUI', 'FailureReason']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for row in dict:
        print (row)
        #print ("end of raw")
        writer.writerow(row)
