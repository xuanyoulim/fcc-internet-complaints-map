import config

import requests
from pathlib import Path
from time import perf_counter

import pandas as pd
from sodapy import Socrata

def coord_to_county(lat, lon):
    ''' Takes in the latitude and longitude coordinates
    and query the FCC API to find the county the coordinates lies within
    returns a dict with county name and county fips, returns None if error'''
    parameters = {'latitude': lat, 'longitude': lon, 'format':'json'}
    try:
        loc_res = requests.get("https://geo.fcc.gov/api/census/block/find", params=parameters)
        ret_dict = loc_res.json()
        c_fips = ret_dict['County']['FIPS']
        county = ret_dict['County']['name']
        return {'county': county, 'c_fips': c_fips}
    except:
        print("Error: getting county from coordinates")
        return None

def generate_ym_total_csv():
    # generate autheticated Socrata client based on api key from 
    client = Socrata("opendata.fcc.gov",
                    config.api_token,
                    username=config.api_key,
                    password=config.api_secret)

    year_start = 2014
    month_start = 10
    year_end = 2014
    month_end = 12
    coord_to_county_dict = {}
    no_coord_counter = 0

    for year in range(year_start, year_end + 1):
        sm = 1
        em = 12
        if year == year_start:
            sm = month_start
        if year == year_end:
            em = month_end
        m_range = range(sm, em+1)
        for month in m_range:
            mo = str(month) if month >= 10 else "0"+str(month)
            ym = f"{year}-{mo}"
            date_start = f"{year}-{mo}-01T00:00:00.000"
            if month == 12:
                date_end = f"{str(year + 1)}-01-01"
            else:
                mo = str(month + 1) if month >= 9 else "0"+str(month+1)
                date_end = f"{str(year)}-{mo}-01"
            query = f"SELECT method, issue, city, state, zip, location_1\
                    WHERE ticket_created >= '{date_start}'\
                    AND ticket_created < '{date_end}'\
                    AND issue_type = 'Internet'"
            results = client.get("3xyp-aqkj", query=query)

            results_df = pd.DataFrame.from_records(results)

            # add column for c_fips by calling coord_to_county
            c_fips = []
            county = []

            for coord in results_df['location_1']:
                try:
                    lat = coord['latitude']
                    lon = coord['longitude']
                    loc_dict = {}
                    if (lat, lon) not in coord_to_county_dict.keys():
                        loc_dict = coord_to_county(coord['latitude'], coord['longitude'])
                        coord_to_county_dict[(lat, lon)] = loc_dict
                    else:
                        loc_dict = coord_to_county_dict[(lat, lon)]
                    c_fips.append(loc_dict['c_fips'])
                    county.append(loc_dict['county'])
                except:
                    no_coord_counter += 1
                    c_fips.append(None)
                    county.append(None)

            results_df['county'] = county
            results_df['c_fips'] = c_fips

            # SELECT c_fips, county name, count
            # generate df for count, group by c_fips
            counts_df = results_df.groupby(['c_fips', 'county', 'state']).size().reset_index(name="total")
            counts_df.set_index('c_fips')

            # get and process county population
            COUNTY_POP = Path('..') / "co-est2019-alldata.csv"
            # COUNTY_POP = "../co-est2019-alldata-csv"
            columns = []
            columns.append('STATE')
            columns.append('COUNTY')
            dtypes={'STATE': 'str', 'COUNTY': 'str'}

            # for year in range(2014, 2020):
            #     col_name = f"POPESTIMATE{str(year)}"
            #     columns.append(col_name)
            columns.append(f"POPESTIMATE{str(year)}")

            county_pop_df = pd.read_csv(COUNTY_POP, dtype=dtypes, usecols=columns)
            county_pop_df['c_fips'] = county_pop_df['STATE'] + county_pop_df['COUNTY']
            county_pop_df.set_index('c_fips')

            # add column for county_pop (or complaints per capita)
            combined_df = pd.merge(counts_df, county_pop_df, on='c_fips')

            # calculate per capita
            # combined_df['per_capita'] = combined_df['total'].astype(float) / combined_df['POPESTIMATE2014'].astype(float)
            combined_df = combined_df.assign(per_capita=combined_df['total']/combined_df[f'POPESTIMATE{str(year)}'])

            downsized_df = combined_df[['c_fips', 'county', 'state', 'total', 'per_capita']]
            # write to csv y-m.csv: c_fips, county name, state(?), count
            # with open("csv/2014-10.csv", mode="w+", newline='') as csvfile:
            write_to_csv = Path('.') / f"csv/{ym}.csv"
            downsized_df.to_csv(write_to_csv, index=False)

generate_ym_total_csv()
