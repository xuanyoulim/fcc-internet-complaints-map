import config

import requests
from pathlib import Path
from time import perf_counter
from datetime import datetime

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

def generate_ym_total_csv(year_start, month_start, year_end, month_end, log=True):
    '''For data from year_start-month_start to year_end-month_end,
    queries fcc api and processes location data (to add county)
    and generates total count by year-month into csv file: year-month.csv'''

    coord_to_county_dict = {} # dict to store location coord to county, fewer api calls

    # variables for sanity checks
    total_no_coord_counter = 0
    total_fcc_block_call = 0
    tic = 0

    # generate autheticated Socrata client based on api key from config
    client = Socrata("opendata.fcc.gov",
                    config.api_token,
                    username=config.api_key,
                    password=config.api_secret)


    for year in range(year_start, year_end + 1):
        # determine range of month in current year
        sm = 1
        em = 12
        if year == year_start:
            sm = month_start
        if year == year_end:
            em = month_end
        m_range = range(sm, em + 1)
        for month in m_range:
            mo = str(month) if month >= 10 else "0"+str(month)
            ym = f"{year}-{mo}"
            date_start = f"{year}-{mo}-01T00:00:00.000"
            # generate date_end for query
            if month == 12:
                date_end = f"{str(year + 1)}-01-01"
            else:
                mo = str(month + 1) if month >= 9 else "0"+str(month+1)
                date_end = f"{str(year)}-{mo}-01"

            # logging
            if log == True:
                print(f"Processing {ym} data...")
                tic = perf_counter()
                issues_processed = 0
            # query api
            count_query = f"SELECT count(*)\
                            WHERE ticket_created >= '{date_start}'\
                            AND ticket_created < '{date_end}'\
                            AND issue_type = 'Internet'"
            count_result = client.get("3xyp-aqkj", query=count_query)
            count = count_result[0]['count']
            query = f"SELECT method, issue, city, state, zip, location_1\
                        WHERE ticket_created >= '{date_start}'\
                        AND ticket_created < '{date_end}'\
                        AND issue_type = 'Internet'\
                        LIMIT {str(count)}"
            results = client.get("3xyp-aqkj", query=query)

            results_df = pd.DataFrame.from_records(results)

            # find out county information for specific location from api call
            c_fips = []
            county = []

            for coord in results_df['location_1']:
                try:
                    lat = coord['latitude']
                    lon = coord['longitude']
                    loc_dict = {}
                    if (lat, lon) not in coord_to_county_dict.keys():
                        loc_dict = coord_to_county(coord['latitude'], coord['longitude'])
                        total_fcc_block_call += 1
                        coord_to_county_dict[(lat, lon)] = loc_dict
                    else:
                        loc_dict = coord_to_county_dict[(lat, lon)]
                    c_fips.append(loc_dict['c_fips'])
                    county.append(loc_dict['county'])
                except:
                    total_no_coord_counter += 1
                    c_fips.append(None)
                    county.append(None)

            # add county information column
            results_df['county'] = county
            results_df['c_fips'] = c_fips

            # SELECT c_fips, county name, state code, count(*), GROUP BY c_fips
            # generate df for count, group by c_fips
            counts_df = results_df.groupby(['c_fips', 'county', 'state']).size().reset_index(name="total")
            counts_df.set_index('c_fips')

            # add county population information into dataframe
            COUNTY_POP = Path('..') / "co-est2019-alldata.csv"
            pop_year = year if year <= 2019 else 2019
            columns = ['STATE', 'COUNTY', f"POPESTIMATE{str(pop_year)}"]
            dtypes={'STATE': 'str', 'COUNTY': 'str'}

            county_pop_df = pd.read_csv(COUNTY_POP, dtype=dtypes, usecols=columns)
            county_pop_df['c_fips'] = county_pop_df['STATE'] + county_pop_df['COUNTY']
            county_pop_df.set_index('c_fips')

            # join on c_fips and calculate per capita
            combined_df = pd.merge(counts_df, county_pop_df, on='c_fips')
            combined_df = combined_df.assign(per_capita=combined_df['total']/combined_df[f'POPESTIMATE{str(pop_year)}'])
            downsized_df = combined_df[['c_fips', 'county', 'state', 'total', 'per_capita']]

            # write to csv y-m.csv: c_fips, county name, state(?), count
            csvfile = Path('.') / f"csv/{ym}.csv"
            downsized_df.to_csv(csvfile, index=False)

            # finish logging
            if log == True:
                toc = perf_counter()
                issues_processed = len(results_df)
                print(f"Finish processing {ym} data. Took {toc - tic:0.2f}s to process {issues_processed} issues.")

    if log == True:
        print(f"Total issues with no coordinates: {total_no_coord_counter}")
        print(f"Total calls to FCC Block API: {total_fcc_block_call}")

if __name__ == "__main__":
    now = datetime.now()
    print(f"Started {str(now)}")
    generate_ym_total_csv(2014, 10, 2020, 6)
    now = datetime.now()
    print(f"Ended {str(now)}")
