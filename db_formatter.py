#!/app/virtualenv/bin/python3
from functions import load_module_config
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
def do_print(_input):
    unique_input = list(set(_input))
    print(f"Processing {len(_input)} lines")
    _ldap_str_format = ''.join([f"({ldap_field}{x})" for x in _input])
    _prefix_str_format = [f"{prefix}{x}" for x in _input]
    # _ldap_str_format = ''.join([f"(cn={x})" for x in _input ])
    db_or_format = ' or '.join([f"'{x}'" for x in _input])
    db_in_format = ','.join([f"'{x}'" for x in _input])
    python_format = ','.join([f"'{x}'" for x in _input])
    json_format = ','.join([f'"{x}"' for x in _input])
    ldap_format = f'(|{_ldap_str_format})'
    prefixed_format = '\n'.join(_prefix_str_format)
    # ldap_format = f'(|{_str_format})'

    print(f"Formatted with Prefix\n{prefixed_format}\n")
    print(f"Formatted for LDAP\n{ldap_format}\n")
    print(f"Formatted for Python\n{python_format}\n")

    print(f"Formatted for DB Or Clause\n{db_or_format}\n")
    print(f"Formatted for DB In Clause\n{db_in_format}\n")
    print(f"Formatted for String\n{','.join(_input)}\n")
    print(f"Distinct values in selection: \n{','.join(unique_input)}\n")
    print(f"Formatted for JSON\n{json_format}\n")
    # print(' or '.join([f"display_name='{x}'" for x in """lines""".splitlines()
    # ]))
    print(f"Formatted without newlines\n{newlines_stripped}")
def _generate_table(lines, delimeter=","):
    table=  "<table>\n"
    table += "<tr>"+"".join([f"<th>{x}</th>" for x in lines[0].split(delimeter)])+"</tr>\n"
    for i in range(1, len(lines)):
        table += "<tr>"+"".join([f"<td>{x}</td>" for x in lines[i].split(delimeter)])+"</tr>\n"
    table += "</table>\n"
    print(table)
column_character = module_config['column_character']
generate_table = module_config['generate_table']
table_header_row = module_config['table_header_row']
use_column= module_config['use_column']
combine_fields = module_config['combine_fields']
combine_columns = module_config['combine_columns']
combine_character = module_config['combine_character']
ldap_field=module_config['ldap_field']
prefix=module_config['prefix']
with open(module_config['data_file']) as f:
    _input=f.read()
    raw_data = _input

newlines_stripped = ' '.join([x.strip()  for x in _input.replace("\n", ' ').replace("\r", '').split(" ") if len(x) > 1])
_input = _input.replace("'", "''").splitlines()
print(len(_input))


#process for columns
new_input = []
for i in _input:
    _line = i.split(column_character)
    if combine_fields:
        tmp = []
        for i in combine_columns:
            tmp.append([x.strip() for x in _line if len(x) > 1][i])

        new_input.append(combine_character.join(tmp))
    else:
        new_input.append([x.strip() for x in _line ][use_column])


_input = new_input


do_print(_input)
unique_input = list(set(_input))
do_print(unique_input)
if generate_table:
    _generate_table(raw_data.split("\n"),column_character)
    pass
print(f"\nProcessed {len(_input)} lines")

