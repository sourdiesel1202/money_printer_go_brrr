import datetime

from functions import read_csv
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

def build_dashboard():
    with open('html/head.html') as f:
        raw_html = f.read()
    with open('html/w3.css') as f:
        css = f.read()
    mpb_Data = read_csv("mpb.csv")
    tabulator_data = build_tabulator_basic_data(mpb_Data)
    raw_html = raw_html.replace("//replace_me_with_output", f"var tabledata = {json.dumps(tabulator_data)}").replace("{{report.name}}", f"MPB Traders Report {max([x[0] for x in mpb_Data[1:]])}")
    raw_html = raw_html.replace("<style></style>", f"<style>{css}</style>")
    with open("dashboard_ready.html", "w+") as f:
        f.write(raw_html)