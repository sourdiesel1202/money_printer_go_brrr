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
    # print(f"output file written to {filename}")
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
    # print(f"Deleted file {filename}")

def generate_csv_string(rows):
    filename = f"tmp{datetime.datetime.now().month}{datetime.datetime.now().day}{datetime.datetime.now().year}{datetime.datetime.now().minute}{datetime.datetime.now().second}{os.getpid()}.csv"
    write_csv(filename,rows)
    res = ""
    with open(filename, "r") as f:
        res = f.read()
    delete_csv(filename)
    return res
def combine_csvs(files):
    _filestr = '\n'.join(files)
    # print(f"Combining the following files {_filestr}")
    records = []
    for _file in files:
        rows= read_csv(_file)
        if len(records) == 0:
            records.append(rows[0])

        for i in range(1, len(rows)):
            records.append(rows[i])
        delete_csv(_file)
    return records
def get_today(module_config):
    if module_config['test_mode']:
        return module_config['test_date']
    else:
        return datetime.datetime.now().strftime("%Y-%m-%d")
def calculate_percentage(x, y):
    try:
        return (float(x)/float(y))*100.00
    except:
        return 0.0
