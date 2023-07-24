import datetime
import os

import boto3
from tqdm import tqdm
import s3
from functions import read_csv, process_list_concurrently
import json
def build_tabulator_basic_data(input_data):
    data = []
    report_attrs = input_data
    # print(report_attrs[0])
    for i in range(1, len(report_attrs)):
        entry = {}
        for ii in range(0, len(report_attrs[i])):
            entry[report_attrs[0][ii]]=report_attrs[i][ii]
        data.append(entry)
    return data

def build_dashboard(module_config):
    with open('html/head.html') as f:
        raw_html = f.read()
    with open('html/w3.css') as f:
        css = f.read()
    mpb_Data = read_csv("mpb.csv")
    # [x.split(".csv")[0] for x in os.listdir(f"{module_config['output_dir']}cached/")]
    tabulator_data = build_tabulator_basic_data(mpb_Data)
    date_string = max([x[0] for x in mpb_Data[1:]])
    type =f"{module_config['timespan_multiplier']} "+module_config['timespan'][0].upper()+module_config['timespan'][1:]
    raw_html = raw_html.replace("//replace_me_with_output", f"var tabledata = {json.dumps(tabulator_data)}").replace("{{report.name}}", f"MPB Traders Report<br>{type}<br>{date_string.split(' ')[0]}<br>{date_string.split(' ')[1]}<br>")
    raw_html = raw_html.replace("<style></style>", f"<style>{css}</style>")
    with open(f"html/dashboard{module_config['timespan_multiplier']}{module_config['timespan']}.html", "w+") as f:
        f.write(raw_html)
    bucketname = 'www.mpb-traders-data.com'
    s3dir = ''

    files = [x for x in os.listdir(f"html/") if f"{module_config['timespan_multiplier']}{module_config['timespan']}" in x]
    totalsize = sum([os.stat(f"html/{f}").st_size for f in files])
    # otalsize = sum([os.stat(f).st_size for f in [x.split(".csv")[ for x in os.listdir(f"html/") if f"{module_config['timespan_multiplier']}{module_config['timespan']}" in x]])
    # totalsize = sum([os.stat(f).st_size for f in files])
    with tqdm(desc='upload', ncols=60,
              total=totalsize, unit='B', unit_scale=1) as pbar:
        s3.fast_upload(boto3.Session(), bucketname, s3dir, files, pbar.update)
    # process_list_concurrently(files, upload_html_concurrently,int(len(files)/module_config['num_processes'])+1 )
    # upload_html_concurrently()
    s3.upload_file(f"html/dashboard{module_config['timespan_multiplier']}{module_config['timespan']}.html", "www.mpb-traders-data.com")

def upload_html_concurrently(files):
    for _file in files:
        print(f"{os.getpid()}: uploading {files.index(_file)}/{len(files)}")
        s3.upload_file(f"html/{_file}","www.mpb-traders-data.com")
    # pass