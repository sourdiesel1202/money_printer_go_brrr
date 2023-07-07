import datetime
import json, csv, os
def load_module_config(module):
    print(f"Loading config file for {module}")
    with open(f"configs/{module}.json", "r") as f:
        return json.loads(f.read())

def write_csv(filename, rows):
    with open(filename  , 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"output file written to {filename}")
    # global_workbook.sheets.append('reports/sheets/'+filename)
def read_csv(filename):
    result = []
    with open(filename,'r', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in spamreader:
            result.append([x for x in row])
    return  result
def delete_csv(filename):
    os.system(f"rm {filename}")
    print(f"Deleted file {filename}")

def generate_csv_string(rows):
    filename = f"tmp{datetime.datetime.now().month}{datetime.datetime.now().day}{datetime.datetime.now().year}{datetime.datetime.now().minute}{datetime.datetime.now().second}.csv"
    write_csv(filename,rows)
    res = ""
    with open(filename, "r") as f:
        res = f.read()
    delete_csv(filename)
    return res