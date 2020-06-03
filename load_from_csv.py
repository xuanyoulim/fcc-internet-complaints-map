import json
import csv
import requests

def load_from_csv():
    # %%
    import csv
    data = []

    with open("../CGBConsumer_Complaints_Data.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    # %%
    output_path = "csv/"
    data_by_month_dict = {} # dict of list of dicts
    no_loc_counter = 0
    no_coord_counter = 0
    for entry in data:
        if entry['Form'] == 'Internet':
            if entry['Location (Center point of the Zip Code)']:
                curr_month_dict = {}
                curr_month_dict['year'] = entry['Ticket Created'][6:10]
                curr_month_dict['month'] = entry['Ticket Created'][:2]
                key = f"{curr_month_dict['year']}-{curr_month_dict['month']}"
                # curr_month_dict['method'] = 
                curr_month_dict['issue'] = entry['Issue']
                try:
                    open_b_index = entry['Location (Center point of the Zip Code)'].index('(')
                    comma_index = entry['Location (Center point of the Zip Code)'].index(',')
                    close_b_index = entry['Location (Center point of the Zip Code)'].index(')')
                    curr_month_dict['x'] = entry['Location (Center point of the Zip Code)'][open_b_index + 1:comma_index]
                    curr_month_dict['y'] = entry['Location (Center point of the Zip Code)'][comma_index + 1:close_b_index]
                    if key not in data_by_month_dict.keys():
                        data_by_month_dict[key] = []
                    data_by_month_dict[key].append(curr_month_dict)
                except:
                    no_coord_counter += 1
            else:
                no_loc_counter += 1
    # a = 1
    loc_county_dict = {}
    # do only october
    ym_start = '2014-10'
    ym_end = '2020-05'
    # ym = "2014-10"
    # generate for year 2014
    for m in range(10, 13):
        total_dict = {}
        ret_dict_list = []
        ym = f'2014-{str(m)}'
        curr_month = data_by_month_dict[ym]
        for entry in curr_month:
            # get county block if haven't gotten it before
            if (entry['x'], entry['y']) not in loc_county_dict.keys():
                parameters = {'latitude': entry['x'], 'longitude':entry['y'], 'format': 'json'}
                loc_res = requests.get("https://geo.fcc.gov/api/census/block/find", params=parameters)
                res_dict = loc_res.json()
                loc_county_dict[(entry['x'], entry['y'])] = res_dict
            else:
                res_dict = loc_county_dict[(entry['x'], entry['y'])]
            index = res_dict['State']['FIPS'] + res_dict['County']['FIPS']
            # entry['c_fips'] = res_dict['County']['FIPS']
            # entry['county'] = res_dict['County']['name']
            # entry['s_fips'] = res_dict['State']['FIPS']
            # entry['state'] = res_dict['State']['name']
            # entry['s_code'] = res_dict['State']['code']
            # entry['index'] = entry['s_fips'] + entry['c_fips']
            total_dict[index] = total_dict.get(index, 0) + 1
        for (index, count) in total_dict.items():
            temp_dict = {}
            temp_dict['index'] = index
            temp_dict['count'] = count
            ret_dict_list.append(temp_dict)
        # write to csv class
        with open(f"{output_path}{ym}.csv", "w+", newline = '') as csvfile:
            # fieldnames = ['year', 'month', 'issue', 'x', 'y', 'c_fips', 'county', 's_fips', 'state', 's_code', 'index']
            fieldnames = ['index', 'count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ret_dict_list)
    # a = 1

load_from_csv()