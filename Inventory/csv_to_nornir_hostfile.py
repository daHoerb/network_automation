# Import the csv library
import csv

# Open the sample csv file and print it to screen
with open("test-file.CSV") as f:
    print (f.read())

# Open the sample csv file, and create a csv.reader object
with open("test-file.csv") as f:
    csv_2_yaml = csv.reader(f, delimiter=";")

    # Loop over each row in csv and leverage the data in yaml
    list = []
    for row in csv_2_yaml:
        device = row[0]
        ip = row[1]
        group = row[2]
        site = row[3]
        platform = row[4]

        list.append ("{0}:\n    hostname: {1}\n    group: {2}\n    site: {3}\n    platform: {4}\n".format(device, ip, group, site, platform))

print (list)

with open("output-host-file.yaml","w+") as w:

    # Loop over each row and write data to file
    w.writelines(list)


