# FCC Complaints Regarding Internet By County Map
*Note: This is developed as part of my final asssignment for COM 461: Data Reporting Spring 2020*

## Data source
The raw data of the complaints submitted to the FCC regarding internet issues is obtained through calls to the [FCC's Consumer Complaints Data API](https://dev.socrata.com/foundry/opendata.fcc.gov/3xyp-aqkj).

The data is then processed using a Python script, [process_data.py](https://github.com/xuanyoulim/fcc-internet-complaints-map/blob/master/process_data.py), that makes calls to the FCC's [Block API](https://geo.fcc.gov/api/census/#!/block/get_block_find) to translate the location coordinates of the center of the zip code that each complaint is submitted from into county FIPS.
At the end, the script generates the total counts of complaints by county for every month from October 2014 to May 2020 and outputs a *.csv* file for each month.

All the *.csv* files can be found in the `csv/` folder and the `log.txt` contains the log for a single run of the script.

### Reflection
At first, I tried processing the data by making calls to the API and storing it in pandas DataFrame for manipulation but it became too complicated. 
Then, I changed my approach to directly process and manipulate a single large csv file that contains all the ~1.7M rows of data. I found the process incredibly slow and inefficient.
In the end, I switched back to the first approach and approached working with pandas through [the lens of SQL](https://pandas.pydata.org/pandas-docs/stable/getting_started/comparison/comparison_with_sql.html).

## Data Analysis
I simply queried the total count of complaints about internet for the month in April 2020, and compared that to March 2020, February 2020, and April 2019 to determine that there was an increase in the count of complaints.

### Reflection
The method I used was simple but flawed. After developing the Python script to process data, I found that the total count of complaints fluctuates by month in general (though April 2020 with 4,286 complaints was the highest in ~2.5 years). 

## Data Visualization
I went with a bubble map made using D3.js that transitions month by month from October 2014 to May 2020 to show the change in the origin of the complaints. The code for bubble map is inspired and modified from D3's own example gallery, https://observablehq.com/@d3/bubble-map. The size of the circle represents the total number of complaints adjusted by the population of each county. 

### Reflection
The map may not be the best representation of the data since a county's population may not necessarily be representative of the county's internet population. On a second take, I would perhaps use a bivariate choropleth map to take into the account of the number of ISPs in each county. Intuitively, I feel that there's a better representation of the data and a better story angle than what I had attempted.
