import config
import pandas as pd
from sodapy import Socrata

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
# client = Socrata("opendata.fcc.gov", None)

# Example authenticated client (needed for non-public datasets):
client = Socrata(opendata.fcc.gov,
                 config.api_token,
                 username=config.api_key,
                 password=config.api_secret)

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("3xyp-aqkj", limit=2000)

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)

